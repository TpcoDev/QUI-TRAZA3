# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Product_template(models.Model):
    _inherit = 'product.template'

    as_contenido_envase = fields.Float(string='Contenido envase', digits=(2, 1))
    as_cantidad_envase = fields.Integer(string='Cantidad de envase')
    as_cantidad_unidades = fields.Integer(string='Cantidad unidades')
    as_type_product = fields.Selection(
        [
            ('MP', 'MP'),
            ('PP', 'PP'),
            ('PT', 'PT'),
        ],
        string="Tipo de Producto Quimetal", default="MP"
    )
