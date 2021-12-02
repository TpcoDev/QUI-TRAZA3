# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
import logging
from psycopg2 import Error, OperationalError
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools.float_utils import float_compare, float_is_zero, float_round

_logger = logging.getLogger(__name__)


class as_stock_production_lot(models.Model):
    _inherit = "stock.production.lot"

    @api.model_create_multi
    def create(self, vals_list):
        res = super(as_stock_production_lot, self).create(vals_list)
        for lot in res:
            lot.name = str(lot.name).upper()
        return res

    @api.onchange('name')
    def as_get_name_upper(self):
        for lot in self:
            lot.name  = str(lot.name).upper()

class as_stock_move_line(models.Model):
    _inherit = "stock.move.line"

    @api.onchange('lot_name')
    def as_name_lot(self):
        for line in self:
            if line.lot_name:
                line.lot_name = str(line.lot_name).upper()

    @api.onchange('product_id', 'product_uom_id')
    def _onchange_product_id(self):
        as_vencimiento = self.expiration_date
        res = super(as_stock_move_line, self)._onchange_product_id()
        self.expiration_date = as_vencimiento
        return res

    @api.depends('product_id', 'picking_type_use_create_lots')
    def _compute_expiration_date(self):
        pass
        # for move_line in self:
        #     if move_line.picking_type_use_create_lots:
        #         if move_line.product_id.use_expiration_date:
        #             move_line.expiration_date = fields.Datetime.today() + datetime.timedelta(days=move_line.product_id.expiration_time)
        #         else:
        #             move_line.expiration_date = False

    @api.onchange('lot_id')
    def _onchange_lot_id(self):
        if not self.picking_type_use_existing_lots or not self.product_id.use_expiration_date:
            return
        if self.lot_id:
            self.expiration_date = self.lot_id.expiration_date
        else:
            self.expiration_date = self.expiration_date

class StockMove(models.Model):
    _inherit = "stock.move"


    def _generate_serial_move_line_commands(self, lot_names, origin_move_line=None):
        """Override to add a default `expiration_date` into the move lines values."""
        as_vencimiento = self.expiration_date
        move_lines_commands = super()._generate_serial_move_line_commands(lot_names, origin_move_line=origin_move_line)
        if self.product_id.use_expiration_date:
            date = fields.Datetime.today() + datetime.timedelta(days=self.product_id.expiration_time)
            for move_line_command in move_lines_commands:
                move_line_vals = move_line_command[2]
                move_line_vals['expiration_date'] = move_line_vals['expiration_date']
        return move_lines_commands
