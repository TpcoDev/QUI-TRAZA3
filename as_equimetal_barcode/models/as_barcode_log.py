# -*- coding: utf-8 -*-
from odoo import models, fields, api,_

class StockProductionLor(models.Model):
    """"creado modelo para verificar que se esta scaneando"""
    _name = 'as.barcode.log'
    _description = 'Heredando modelo de lote'

    name = fields.Char(string='barcode')
    as_json = fields.Char(string='json respuesta')


class StockProductionLor(models.Model):
    """"creado modelo para verificar que se esta scaneando"""
    _inherit = 'stock.production.lot'

    create_date = fields.Datetime('Fecha de Creación', index=False, readonly=False)
