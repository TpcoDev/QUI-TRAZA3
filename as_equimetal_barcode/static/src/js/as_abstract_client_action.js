odoo.define('as_equimetal_barcode.as_ClientAction', function (require) {
    'use strict';
    console.log('ENTRO A CLIENTQ')
    var ClientAction = require('stock_barcode.ClientAction');

    var concurrency = require('web.concurrency');
    var core = require('web.core');
    var AbstractAction = require('web.AbstractAction');
    var BarcodeParser = require('barcodes.BarcodeParser');

    var ViewsWidget = require('stock_barcode.ViewsWidget');
    var HeaderWidget = require('stock_barcode.HeaderWidget');
    var LinesWidget = require('stock_barcode.LinesWidget');
    var SettingsWidget = require('stock_barcode.SettingsWidget');
    var utils = require('web.utils');
    var _t = core._t;
    var vals_resp

    function urlParam2(name) {
        var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
        if (results == null) {
            return null;
        }
        return decodeURI(results[1]) || 0;
    }

    function searchReadGS1(barcode) {
        console.log('Enro aqui tercero' + barcode)
        var urlcadena = window.location.origin + '/quimetal/barcode' + '?barcode=' + barcode;
        console.log(urlcadena);
        window.vals_resp = ''
        $.ajax({
            url: urlcadena,
            success: function (respuesta) {
                var obj = JSON.parse(respuesta);
                window.vals_resp = obj;

            },
            error: function () {
                console.log("No se ha podido obtener la información");
                window.vals_resp = {
                    'type': false,
                    'barcode': barcode,
                    'product': false,
                };
            }
        });
        return vals_resp;

    }
    var as_ClientAction = ClientAction.include({

        events: {
            'click .o_barman': '_asBarcode',
            'change .o_search_barman': '_asAutoSearchBarcode',
        },

        /**
         * Handles the `add_product` OdooEvent. It destroys `this.linesWidget` and displays an instance
         * of `ViewsWidget` for the line model.
         * `this.ViewsWidget`
         *
         * @private
         * @param {OdooEvent} ev
         */
        _asBarcode: function (ev) {
            var barcode = $('#barman').val();
            console.log("barcode:" + barcode);
            this._onBarcodeScannedHandler(barcode);
        },
        _asAutoSearchBarcode: function (ev) {
            var barcode = $('#barman').val();
            localStorage.setItem("linea_id", "");

            console.log("barcode:" + barcode);

            this._onBarcodeScannedHandler(barcode);
            // Recuperar el ID de la linea creada o seleccionada
            // var id = $(ev.target).parents('.o_barcode_line').data('id');

            setTimeout(function () {
                var id = localStorage.getItem("linea_id");
                console.log("id:" + id);
                $('.o_barcode_line').each(function (i, obj) {
                    // console.log("LL" + obj.innerHTML);
                    var theid = $(this).attr("data-id");
                    console.log(theid);

                    if (theid == id) {
                        $(this).find("a").click();
                        console.log("editando");
                        setTimeout(function () {
                            $("input[name='qty_done']").select();
                        }, 1500);
                    }
                });
            }, 2000);

        },

        /**
         * Loop over the lines displayed in the current pages and try to find a candidate to increment
         * according to the `params` argument.
         *
         * @private
         * @param {Object} params information needed to find the candidate line
         * @param {Object} params.product
         * @param {Object} params.lot_id
         * @param {Object} params.lot_name
         * @returns object|boolean line or false if nothing match
         */
        _findCandidateLineToIncrement: function (params) {
            var product = params.product;
            var lotId = params.lot_id;
            var lotName = params.lot_name;
            var packageId = params.package_id;
            var currentPage = this.pages[this.currentPageIndex];
            var res = false;
            for (var z = 0; z < currentPage.lines.length; z++) {
                var lineInCurrentPage = currentPage.lines[z];
                if (lineInCurrentPage.product_id.id === product.id) {
                    // If the line is empty, we could re-use it.
                    if (lineInCurrentPage.virtual_id &&
                        (this.actionParams.model === 'stock.picking' &&
                        ! lineInCurrentPage.qty_done &&
                        ! lineInCurrentPage.product_uom_qty &&
                        ! lineInCurrentPage.lot_id &&
                        ! lineInCurrentPage.lot_name &&
                        ! lineInCurrentPage.package_id
                        ) ||
                        (this.actionParams.model === 'stock.inventory' &&
                        ! lineInCurrentPage.product_qty &&
                        ! lineInCurrentPage.prod_lot_id
                        )
                    ) {
                        res = lineInCurrentPage;
                        break;
                    }

                    if (product.tracking === 'serial' &&
                        ((this.actionParams.model === 'stock.picking' &&
                        lineInCurrentPage.qty_done > 0 && this.requireLotNumber
                        ) ||
                        (this.actionParams.model === 'stock.inventory' &&
                        lineInCurrentPage.product_qty > 0
                        ))) {
                        continue;
                    }
                    // if (lineInCurrentPage.qty_done &&
                    // (this.actionParams.model === 'stock.inventory' ||
                    // lineInCurrentPage.location_dest_id.id === currentPage.location_dest_id) &&
                    // this.scannedLines.indexOf(lineInCurrentPage.virtual_id || lineInCurrentPage.id) === -1 &&
                    // lineInCurrentPage.qty_done >= lineInCurrentPage.product_uom_qty) {
                    //     continue;
                    // }
                    if (lotId &&
                        ((this.actionParams.model === 'stock.picking' &&
                        lineInCurrentPage.lot_id &&
                        lineInCurrentPage.lot_id[0] !== lotId
                        ) ||
                        (this.actionParams.model === 'stock.inventory' &&
                        lineInCurrentPage.prod_lot_id &&
                        lineInCurrentPage.prod_lot_id[0] !== lotId
                        )
                    )) {
                        continue;
                    }
                    if (lotName &&
                        lineInCurrentPage.lot_name &&
                        lineInCurrentPage.lot_name !== lotName
                        ) {
                        continue;
                    }
                    if (packageId &&
                        (! lineInCurrentPage.package_id ||
                        lineInCurrentPage.package_id[0] !== packageId[0])
                        ) {
                        continue;
                    }
                    // if(lineInCurrentPage.product_uom_qty && lineInCurrentPage.qty_done >= lineInCurrentPage.product_uom_qty) {
                    //     continue;
                    // }
                    res = lineInCurrentPage;
                    break;
                }
            }
            return res;
        },
        /**
         * Main method called when a quantity needs to be incremented or a lot set on a line.
         * it calls `this._findCandidateLineToIncrement` first, if nothing is found it may use
         * `this._makeNewLine`.
         *
         * @private
         * @param {Object} params information needed to find the potential candidate line
         * @param {Object} params.product
         * @param {Object} params.lot_id
         * @param {Object} params.lot_name
         * @param {Object} params.package_id
         * @param {Object} params.result_package_id
         * @param {Boolean} params.doNotClearLineHighlight don't clear the previous line highlight when
         *     highlighting a new one
         * @return {object} object wrapping the incremented line and some other informations
         */
        _incrementLines: function (params) {
            var line = this._findCandidateLineToIncrement(params);
            var isNewLine = false;
            if (line) {
                // Update the line with the processed quantity.
                if (params.product.tracking === 'none' ||
                    params.lot_id ||
                    params.lot_name ||
                    !this.requireLotNumber
                    ) {
                    if (this._isPickingRelated()) {
                        line.qty_done += 0;
                        if (params.package_id) {
                            line.package_id = params.package_id;
                        }
                        if (params.result_package_id) {
                            line.result_package_id = params.result_package_id;
                        }
                    } else if (this.actionParams.model === 'stock.inventory') {
                        line.product_qty += 0;
                    }
                }
            } else if (this._isAbleToCreateNewLine() && this.currentState.picking_type_id[0]==18) {
                isNewLine = true;
                // Create a line with the processed quantity.
                if (params.product.tracking === 'none' ||
                    params.lot_id ||
                    params.lot_name ||
                    !this.requireLotNumber
                    ) {
                    params.qty_done = 0;
                } else {
                    params.qty_done = 0;
                }
                line = this._makeNewLine(params);
                this._getLines(this.currentState).push(line);
                this.pages[this.currentPageIndex].lines.push(line);
            }
            if (this._isPickingRelated()) {
                if (params.lot_id) {
                    line.lot_id = [params.lot_id];
                }
                if (params.lot_name) {
                    line.lot_name = params.lot_name;
                }
            } else if (this.actionParams.model === 'stock.inventory') {
                if (params.lot_id) {
                    line.prod_lot_id = [params.lot_id, params.lot_name];
                }
            }
            return {
                'id': line.id,
                'virtualId': line.virtual_id,
                'lineDescription': line,
                'isNewLine': isNewLine,
            };
        },
        start: function () {
            var self = this;
            // this.$('.o_content').addClass('o_barcode_client_action');
            // core.bus.on('barcode_scanned', this, this._onBarcodeScannedHandler);

            this.headerWidget = new HeaderWidget(this);
            this.settingsWidget = new SettingsWidget(this, this.actionParams.model, this.mode, this.allow_scrap);
            return this._super.apply(this, arguments).then(function () {
                return Promise.all([
                    self.headerWidget.prependTo(self.$('.o_content')),
                    self.settingsWidget.appendTo(self.$('.o_content'))
                ]).then(function () {
                    self.settingsWidget.do_hide();
                    return self._save();
                }).then(function () {
                    return self._reloadLineWidget(self.currentPageIndex);
                });
            });
        },

        /**
         * Handles the barcode scan event. Dispatch it to the appropriate method if it is a
         * commande, else use `this._onBarcodeScanned`.
         *
         * @private
         * @param {String} barcode scanned barcode
         */
        _onBarcodeScannedHandler: function (barcode) {
            var resultado = {}
            var self = this;
            this.barcode_producto = '';
            var existe_order = true
            var existe_page = true
            self.requireLotNumber = true;
            localStorage.setItem("as_product_type", "");
            localStorage.setItem("as_product_barcode", "");
            // localStorage.setItem("as_product_code", "");
            var debug_gs1 = urlParam2('debug_gs1');
            if (debug_gs1) {
                barcode = debug_gs1;
                // alert(debug_gs1)
            }
            var create_lot = false
            if (self.currentState.picking_type_id[0] != 18){
                create_lot = true
            }
            // barcode = '104443391MPQUI01117210308';
            //llamando a endpoint barcode
            var urlcadena = window.location.origin + '/quimetal/barcode' + '?barcode=' + barcode +'&create='+ create_lot;


            $.ajax({
                url: urlcadena,
                global: false,
                async: false,
                success: function (respuesta) {
                    window.val1 = JSON.parse(respuesta);
                    vals_resp = JSON.parse(respuesta);
                    console.log('IDs: ' + (vals_resp.result))
                    // alert(vals_resp.result)

                },
                error: function () {
                    console.log("No se ha podido obtener la información");
                    vals_resp = {
                        'type': false,
                        'barcode': barcode,
                        'product': false,
                    };
                }
            });
            resultado = vals_resp;
            console.log('resultado: ' + JSON.stringify(resultado));
            if (resultado.type) {
                barcode = resultado.lote;
                $('#as_barcode_scanned').text(vals_resp.barcode);
                $('#as_barcode_scanned2').text(vals_resp.result);
                $('#barman').val("");
            } else {
                $('#as_barcode_scanned').text(barcode);
                $('#as_barcode_scanned2').text("");
                $('#barman').val("");
            }
            
            // this.barcode_producto = resultado.product
            
            localStorage.setItem("as_product_type", resultado.product_type);
            localStorage.setItem("as_product_barcode", resultado.gtin);
            // localStorage.setItem("as_product_code", resultado.code);

            var as_barcode = localStorage.getItem("as_product_barcode");
            var lines_with_lot = _.filter(self.currentState.move_line_ids, function (line) {
                return ((line.lot_id && line.lot_id[1] === barcode) || line.lot_name === barcode) && line.product_id.barcode == as_barcode;
            });
            if (lines_with_lot<=0) {
                existe_order = false
            }
            // existe en la page
            if(this.pages.length > 1){
                var currentPage = this.pages[this.currentPageIndex]
                var lines_page_lot = _.filter(self.currentState.move_line_ids, function (line) {
                    return ((line.lot_id && line.lot_id[1] === barcode && line.location_dest_id['id'] == currentPage.location_dest_id) || (line.lot_name === barcode && line.location_dest_id['id'] == currentPage.location_dest_id)) && line.product_id.barcode == as_barcode;
                });
                if (lines_page_lot<=0) {
                    existe_page = false
                }

            }

            this.mutex.exec(function () {
                if (self.mode === 'done' || self.mode === 'cancel') {
                    self.do_warn(false, _t('Scanning is disabled in this state'));
                    return Promise.resolve();
                }
                if (!resultado.product) {
                    self.do_warn(false, _t('PRODUCTO NO ESTA EN EL SISTEMA, DEBE CREARLO'));
                    return Promise.resolve();
                }
                if (self.currentState.picking_type_id[0] != 18){
                    if (!existe_order && !resultado.existe) {
                        self.do_warn(false, _t('PRODUCTO-LOTE NO ESTA EN EL SISTEMA'));
                        return Promise.resolve();
                    }
                    if (!existe_order) {
                        self.do_warn(false, _t('PRODUCTO-LOTE NO ESTA EN LA ORDEN'));
                        return Promise.resolve();
                    }
                    
                }
                if (!existe_page) {
                    self.do_warn(false, _t('PRODUCTO-LOTE NO EN ESTA PAGINA, CLICK EN SIGUIENTE O ANTERIOR'));
                    return Promise.resolve();
                }
                var commandeHandler = self.commands[barcode];
                if (commandeHandler) {
                    return commandeHandler();
                }
                return self._onBarcodeScanned(barcode).then(function () {
                    // FIXME sle: not the right place to do that
                    if (self.show_entire_packs && self.lastScannedPackage) {
                        return self._reloadLineWidget(self.currentPageIndex);
                    }
                });
            });
        },

        /**
         * Handle what needs to be done when a product is scanned.
         *
         * @param {string} barcode scanned barcode
         * @param {Object} linesActions
         * @returns {Promise}
         */
        _step_product: async function (barcode, linesActions) {
            var self = this;
            this.currentStep = 'product';
            this.stepState = $.extend(true, {}, this.currentState);
            var errorMessage;

            var product = await this._isProduct(barcode);
            if (product) {
                if (product.tracking !== 'none' && self.requireLotNumber) {
                    this.currentStep = 'lot';
                }
                var res = this._incrementLines({
                    'product': product,
                    'barcode': barcode
                });
                console.log("resres:" + JSON.stringify(res.id));
                localStorage.setItem("linea_id", res.id);
                if (res.isNewLine) {
                    if (this.actionParams.model === 'stock.inventory') {
                        // FIXME sle: add owner_id, prod_lot_id, owner_id, product_uom_id
                        return this._rpc({
                            model: 'product.product',
                            method: 'get_theoretical_quantity',
                            args: [
                                res.lineDescription.product_id.id,
                                res.lineDescription.location_id.id,
                            ],
                        }).then(function (theoretical_qty) {
                            res.lineDescription.theoretical_qty = theoretical_qty;
                            linesActions.push([self.linesWidget.addProduct, [res.lineDescription, self.actionParams.model]]);
                            self.scannedLines.push(res.id || res.virtualId);
                            return Promise.resolve({
                                linesActions: linesActions
                            });
                        });
                    } else {
                        linesActions.push([this.linesWidget.addProduct, [res.lineDescription, this.actionParams.model]]);
                    }
                } else if (!(res.id || res.virtualId)) {
                    return Promise.reject(_t("There are no lines to increment."));
                } else {
                    if (product.tracking === 'none' || !self.requireLotNumber) {
                        linesActions.push([this.linesWidget.incrementProduct, [res.id || res.virtualId, product.qty || 1, this.actionParams.model]]);
                    } else {
                        linesActions.push([this.linesWidget.incrementProduct, [res.id || res.virtualId, 0, this.actionParams.model]]);
                    }
                }
                this.scannedLines.push(res.id || res.virtualId);
                return Promise.resolve({
                    linesActions: linesActions
                });
            } else {
                var success = function (res) {
                    return Promise.resolve({
                        linesActions: res.linesActions
                    });
                };
                var fail = function (specializedErrorMessage) {
                    self.currentStep = 'product';
                    if (specializedErrorMessage) {
                        return Promise.reject(specializedErrorMessage);
                    }
                    if (!self.scannedLines.length) {
                        if (self.groups.group_tracking_lot) {
                            errorMessage = _t("You are expected to scan one or more products or a package available at the picking's location");
                        } else {
                            errorMessage = _t('You are expected to scan one or more products.');
                        }
                        return Promise.reject(errorMessage);
                    }

                    var destinationLocation = self.locationsByBarcode[barcode];
                    if (destinationLocation) {
                        return self._step_destination(barcode, linesActions);
                    } else {
                        errorMessage = _t('You are expected to scan more products or a destination location.');
                        return Promise.reject(errorMessage);
                    }
                };
                return self._step_lot(barcode, linesActions).then(success, function () {
                    return self._step_package(barcode, linesActions).then(success, fail);
                });
            }
        },

        /**
         * Handle what needs to be done when a lot is scanned.
         *
         * @param {string} barcode scanned barcode
         * @param {Object} linesActions
         * @returns {Promise}
         */
        _step_lot: async function (barcode, linesActions) {
            if (!this.groups.group_production_lot || !this.requireLotNumber) {
                return Promise.reject();
            }
            this.currentStep = 'lot';
            this.stepState = $.extend(true, {}, this.currentState);
            var errorMessage;
            var self = this;

            // Bypass this step if needed.
            var product = await this._isProduct(barcode);
            if (product) {
                return this._step_product(barcode, linesActions);
            } else if (this.locationsByBarcode[barcode]) {
                return this._step_destination(barcode, linesActions);
            }

            var getProductFromLastScannedLine = function () {
                if (self.scannedLines.length) {
                    var idOrVirtualId2 = self.scannedLines[self.scannedLines.length + 1];
                    var idOrVirtualId = self.scannedLines[self.scannedLines.length - 1];
                    var line = _.find(self._getLines(self.currentState), function (line) {
                        return line.virtual_id === idOrVirtualId || line.id === idOrVirtualId;
                    });
                    if (line) {
                        var product = self.productsByBarcode[line.product_barcode || line.product_id.barcode];
                        // Product was added by lot or package
                        if (!product) {
                            return false;
                        }
                        product.barcode = line.product_barcode || line.product_id.barcode;
                        return product;
                    }
                }
                return false;
            };

            var getProductFromCurrentPage = function () {
                return _.map(self.pages[self.currentPageIndex].lines, function (line) {
                    return line.product_id.id;
                });
            };

            var getProductFromOperation = function () {
                return _.map(self._getLines(self.currentState), function (line) {
                    return line.product_id.id;
                });
            };

            var readProductQuant = function (product_id, lots) {
                var advanceSettings = self.groups.group_tracking_lot || self.groups.group_tracking_owner;
                var product_barcode = _.findKey(self.productsByBarcode, function (product) {
                    return product.id === product_id;
                });
                var product = false;
                var prom = Promise.resolve();

                if (product_barcode) {
                    product = self.productsByBarcode[product_barcode];
                    product.barcode = product_barcode;
                }

                if (!product || advanceSettings) {
                    var lot_ids = _.map(lots, function (lot) {
                        return lot.id;
                    });
                    prom = self._rpc({
                        model: 'product.product',
                        method: 'read_product_and_package',
                        args: [product_id],
                        kwargs: {
                            lot_ids: advanceSettings ? lot_ids : false,
                            fetch_product: !(product),
                        },
                    });
                }

                return prom.then(function (res) {
                    product = product || res.product;
                    var lot = _.find(lots, function (lot) {
                        return lot.product_id[0] === product.id;
                    });
                    var data = {
                        lot_id: lot.id,
                        lot_name: lot.display_name,
                        product: product
                    };
                    if (res && res.quant) {
                        data.package_id = res.quant.package_id;
                        data.owner_id = res.quant.owner_id;
                    }
                    return Promise.resolve(data);
                });
            };

            var getLotInfo = function (lots) {
                var products_in_lots = _.map(lots, function (lot) {
                    return lot.product_id[0];
                });
                var products = getProductFromLastScannedLine();
                var product_id = _.intersection(products, products_in_lots);
                if (!product_id.length) {
                    products = getProductFromCurrentPage();
                    product_id = _.intersection(products, products_in_lots);
                }
                if (!product_id.length) {
                    products = getProductFromOperation();
                    product_id = _.intersection(products, products_in_lots);
                }
                if (!product_id.length) {
                    product_id = [lots[0].product_id[0]];
                }
                return readProductQuant(product_id[0], lots);
            };

            var searchRead = function (barcode) {
                // Check before if it exists reservation with the lot.

                var as_tipo = localStorage.getItem("as_product_type");
                var as_barcode = localStorage.getItem("as_product_barcode");
                // var as_code = localStorage.getItem("as_product_code");
                    var lines_with_lot = _.filter(self.currentState.move_line_ids, function (line) {
                        return ((line.lot_id && line.lot_id[1] === barcode) || line.lot_name === barcode) && line.product_id.barcode == as_barcode;
                    });
            
                var line_with_lot;
                if (lines_with_lot.length > 0) {
                    lines_with_lot[0].id
                    var line_index = 0;
                    // Get last scanned product if several products have the same lot name
                    var last_product = lines_with_lot.length > 1 && getProductFromLastScannedLine();
                    if (last_product) {
                        var last_product_index = _.findIndex(lines_with_lot, function (line) {
                            return line.product_id && line.product_id.id === last_product.id;
                        });
                        if (last_product_index > -1) {
                            line_index = last_product_index;
                        }
                    }
                    line_with_lot = lines_with_lot[line_index];
                }
                var def;
                if (line_with_lot) {
                    def = Promise.resolve([{
                        name: barcode,
                        display_name: barcode,
                        id: line_with_lot.lot_id[0],
                        product_id: [line_with_lot.product_id.id, line_with_lot.display_name],
                    }]);
                } else {
                    def = self._rpc({
                        model: 'stock.production.lot',
                        method: 'search_read',
                        domain: [
                            ['name', '=', barcode],['product_id.barcode','=',as_barcode]
                        ],
                    });
            
                }
                return def.then(function (res) {
                    if (!res.length) {
                        errorMessage = _t('The scanned lot does not match an existing one.');
                        return Promise.reject(errorMessage);
                    }
                    return getLotInfo(res);
                });
            };

            var create = function (barcode, product) {
                return self._rpc({
                    model: 'stock.production.lot',
                    method: 'create',
                    args: [{
                        'name': barcode,
                        'product_id': product.id,
                        'company_id': self.currentState.company_id[0],
                    }],
                });
            };

            var def;
            if (this.currentState.use_create_lots &&
                !this.currentState.use_existing_lots) {
                // Do not create lot if product is not set. It could happens by a
                // direct lot scan from product or source location step.
                var product = getProductFromLastScannedLine();
                if (!product || product.tracking === "none") {
                    return Promise.reject();
                }
                def = Promise.resolve({
                    lot_name: barcode,
                    product: product
                });
            } else if (!this.currentState.use_create_lots &&
                this.currentState.use_existing_lots) {
                def = searchRead(barcode);
            } else {
                def = searchRead(barcode).then(function (res) {
                    return Promise.resolve(res);
                }, function (errorMessage) {
                    var product = getProductFromLastScannedLine();
                    if (product && product.tracking !== "none") {
                        return create(barcode, product).then(function (lot_id) {
                            return Promise.resolve({
                                lot_id: lot_id,
                                lot_name: barcode,
                                product: product
                            });
                        });
                    }
                    return Promise.reject(errorMessage);
                });
            }
            return def.then(function (lot_info) {
                var product = lot_info.product;
                if (product.tracking === 'serial' && self._lot_name_used(product, barcode)) {
                    errorMessage = _t('The scanned serial number is already used.');
                    return Promise.reject(errorMessage);
                }
                var res = self._incrementLines({
                    'product': product,
                    'barcode': lot_info.product.barcode,
                    'lot_id': lot_info.lot_id,
                    'lot_name': lot_info.lot_name,
                    'owner_id': lot_info.owner_id,
                    'package_id': lot_info.package_id,
                });
                if (res.isNewLine) {
                    localStorage.setItem("linea_id", res.lineDescription.virtual_id);

                    function handle_line() {
                        self.scannedLines.push(res.lineDescription.virtual_id);
                        linesActions.push([self.linesWidget.addProduct, [res.lineDescription, self.actionParams.model]]);
                    }

                    if (self.actionParams.model === 'stock.inventory') {
                        // TODO deduplicate: this code is almost the same as in _step_product
                        return self._rpc({
                            model: 'product.product',
                            method: 'get_theoretical_quantity',
                            args: [
                                res.lineDescription.product_id.id,
                                res.lineDescription.location_id.id,
                                res.lineDescription.prod_lot_id[0],
                            ],
                        }).then(function (theoretical_qty) {
                            res.lineDescription.theoretical_qty = theoretical_qty;
                            handle_line();
                            return Promise.resolve({
                                linesActions: linesActions
                            });
                        });
                    }
                    handle_line();

                } else {
                    localStorage.setItem("linea_id", res.lineDescription.id || res.lineDescription.virtual_id);
                    if (self.scannedLines.indexOf(res.lineDescription.id) === -1) {
                        self.scannedLines.push(res.lineDescription.id || res.lineDescription.virtual_id);
                    }
                    linesActions.push([self.linesWidget.incrementProduct, [res.id || res.virtualId, 1, self.actionParams.model]]);
                    linesActions.push([self.linesWidget.setLotName, [res.id || res.virtualId, barcode]]);
                }
                return Promise.resolve({
                    linesActions: linesActions
                });
            });
        },

    });
    core.action_registry.add('stock_barcode.stock_barcode_client_action', as_ClientAction);
    return as_ClientAction;

});