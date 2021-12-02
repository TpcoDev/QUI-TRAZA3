# -*- coding: utf-8 -*-
from odoo import models, fields, api,_

class AsMessageLog(models.Model):
    _name = 'as.webservice.logs'
    _description = 'Logs para webservice'
    _order = 'create_date desc'
        
    name = fields.Char(string='Webservice (method)')
    as_token = fields.Char(string='Token')
    as_fecha = fields.Datetime(string='Fecha')
    as_json = fields.Char(string='Json')
    state = fields.Char(string='Estado')
    as_motivo = fields.Char(string='Observación')