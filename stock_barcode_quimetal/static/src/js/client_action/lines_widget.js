odoo.define('stock_barcode.QuimetalLinesWidget', function (require) {
    'use strict';

    var LinesWidget = require('stock_barcode.LinesWidget');

    var QuimetalLinesWidget = LinesWidget.include({
        events: _.extend({}, LinesWidget.prototype.events, {
            'click .o_print': '_onClickPrintLine',
        }),
        /**
         * Handles the click on the `edit button` on a line.
         *
         * @private
         * @param {jQuery.Event} ev
         */
        _onClickPrintLine: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            var id = $(ev.target).parents('.o_barcode_line').data('id');
            console.log('id', id, ' => ', this);
            this.trigger_up('print_line', {id: id});
        },
    });

    return QuimetalLinesWidget;

});
