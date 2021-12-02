# -*- coding: utf-8 -*-
from odoo import models, fields, api

class StockMoveLine(models.Model):
    _inherit = 'stock.location'

    as_plantilla = fields.Selection([
        ('1', 'Destino = QA'),
        ('2', 'Origen = QA'),],
        'Plantilla de Correo',default='1')