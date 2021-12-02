# -*- coding: utf-8 -*-
from odoo import models, fields, api,_

class StockProductionLor(models.Model):
    _inherit = 'stock.production.lot'
    _description = 'Heredando modelo de lote'
