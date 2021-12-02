from odoo import fields, models, api


class Uom(models.Model):
    _inherit = 'uom.uom'

    unidad_sap = fields.Selection(selection=[('BI', 'BI'), ('BO', 'BO')])
    as_contenido_envase = fields.Char()
