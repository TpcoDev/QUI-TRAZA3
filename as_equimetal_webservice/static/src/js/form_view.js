odoo.define('as_equimetal_webservice.extension_name', function (require) {
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
});