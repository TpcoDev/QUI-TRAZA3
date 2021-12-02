# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    f_closed = fields.Boolean(default=False)
    as_num_comex = fields.Char(string='NUM-COMEX')
