from odoo import fields, models, api


class Uom(models.Model):
    _inherit = 'uom.uom'

    unidad_sap = fields.Char()
    as_contenido_envase = fields.Char()
