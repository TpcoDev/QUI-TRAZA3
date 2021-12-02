# -*- coding: utf-8 -*-
from odoo import models, fields, api


class Embalaje(models.Model):
    _name = 'quimetal.embalaje'

    name = fields.Char()
    cod_embalaje = fields.Char()
    active = fields.Boolean(default=True)


class UnidadLogisticas(models.Model):
    _name = 'quimetal.unid.logisticas'

    name = fields.Char(string='Name', required=False)
    cod_unid = fields.Char()
    active = fields.Boolean(default=True)


class Envases(models.Model):
    _name = 'quimetal.envases'
    _description = 'Quimetal Envases'

    name = fields.Char()
    cod_envase = fields.Char()
    active = fields.Boolean(default=True)


class Product_template(models.Model):
    _inherit = 'product.template'

    # Nuevos campos
    envase_id = fields.Many2one(comodel_name='quimetal.envases', string='Envase')
    embalaje_id = fields.Many2one(comodel_name='quimetal.embalaje', string='Embalaje')
    unidad_logistica_id = fields.Many2one(comodel_name='quimetal.unid.logisticas', string='Logistica')
    unidad_referencia = fields.Many2one(comodel_name='uom.uom', domain=[('name', 'in', ('LT', 'KG'))],
                                        string='Unidad Referencia')
