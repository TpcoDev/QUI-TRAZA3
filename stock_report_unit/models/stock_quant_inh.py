# -*- coding: utf-8 -*-

import logging

from psycopg2 import Error, OperationalError

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools.float_utils import float_compare, float_is_zero, float_round

_logger = logging.getLogger(__name__)


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    # unit_ref
    unit_ref = fields.Char(compute='compute_unit', string='Unit.')
    cant = fields.Float(string='Cant.', required=False, compute="compute_cant")

    def compute_cant(self):
        for record in self:
            record.cant = record.inventory_quantity / record.product_uom_id.factor

    # def compute_unit(self):
    #     for record in self:
    #         record.unit_ref = record.product_id.product_tmpl_id.unidad_referencia.name

    def compute_unit(self):
        uom_all= self.env['uom.uom'].search([])
        for record in self:
            oum_obj=uom_all.filtered(lambda uo: uo.category_id.id==record.product_uom_id.category_id.id and uo.uom_type=="reference")
            record.unit_ref=oum_obj.name