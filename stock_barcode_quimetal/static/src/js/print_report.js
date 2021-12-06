odoo.define('stock_barcode_quimetal.print_report', function (require) {
    "use strict";

    var AbstractController = require('web.AbstractController');
    var config = require('web.config');
    var core = require('web.core');
    var dialogs = require('web.view_dialogs');
    var utils = require('web.utils');
    var session = require("web.session");
    var Dialog = require('web.Dialog');
    var qweb = core.qweb;
    var _t = core._t;
    var FormController = require('web.FormController');
    var FormRenderer = require('web.FormRenderer');


    FormRenderer.include({
        events: _.extend({}, FormRenderer.prototype.events, {
            'click .o_print_report': '_onPrintReport',
        }),

        _onPrintReport: function (ev) {
            var self = this;
            debugger;
            ev.preventDefault();

            this._rpc({
                route: "/stock_barcode_quimetal/print_label",
                params: {
                    'id': self.state.data.id
                }
            }).then(function (data) {
                console.log(data);
                if (data['print'] === true) {
                    var pdf = 'data:application/pdf;base64,' + data['bytes'];
                    // Insert a link that allows the user to download the PDF file
                    var link = document.createElement('a');
                    link.innerHTML = 'Download PDF file';
                    link.download = 'Etiquetas.pdf';
                    link.href = pdf;
                    link.click();
                } else {
                    alert("No se pudo imprimir");
                }


            });

        }

    });

    FormController.include({
        updateButtons: function () {
            this._super.apply(this, arguments)
            if (this.modelName === 'purchase.order' || this.modelName === 'sale.order' || this.modelName === 'stock.picking') {
                const record = this.model.get(this.handle, {raw: false});
                if (record.data.f_closed === 1) {
                    this.$buttons.find('.o_form_button_edit').hide();
                } else {
                    this.$buttons.find('o_form_button_edit').show()
                }
            }
        }
    })
})
;