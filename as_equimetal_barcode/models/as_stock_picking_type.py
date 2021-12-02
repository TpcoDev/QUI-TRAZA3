# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class PickingType(models.Model):
    _inherit = "stock.picking.type"

    as_despacho = fields.Boolean(string='Operacion= Transferencia Despacho?')