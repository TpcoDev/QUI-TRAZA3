import base64
import logging
import os
import shutil
import tempfile
from io import BytesIO
from datetime import datetime
import barcode
from barcode.writer import ImageWriter

from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class Lines(models.Model):
    _name = 'stock.quimetal.lines'

    line_id = fields.Many2one(comodel_name='stock.move.line', string='Line')
    num_bultos = fields.Integer(string='Numero de Bultos', required=True, default=1)
    cant_envases = fields.Integer(string='Cantidad de Envases', required=True, default=1)
    peso_envase = fields.Float(string='Peso/Envase', required=True, default=1)

    @api.constrains('num_bultos', 'cant_envases', 'peso_envase')
    def _check_zero(self):
        if self.num_bultos <= 0 or self.cant_envases <= 0 or self.peso_envase <= 0:
            raise UserError('No puede ser menor o igual a 0')


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'
    _description = 'Description'

    quimetal_lines_ids = fields.One2many(
        comodel_name='stock.quimetal.lines', inverse_name='line_id',
        string='Quimetal lines', required=False
    )

    total_cant_envases = fields.Integer(compute='_compute_total_cant_envases', string='Total Cantidad de Envases')
    total_peso_envase = fields.Float(compute='_compute_total_peso_envase', string='Total Peso/Envase')

    @api.depends('quimetal_lines_ids.cant_envases')
    def _compute_total_cant_envases(self):
        for rec in self:
            rec.total_cant_envases = sum(rec.quimetal_lines_ids.mapped('cant_envases'))

    @api.depends('quimetal_lines_ids.peso_envase', 'quimetal_lines_ids.cant_envases', 'quimetal_lines_ids.num_bultos')
    def _compute_total_peso_envase(self):
        sum_list = []
        for rec in self:
            for line in rec.quimetal_lines_ids:
                sum_list.append(line.peso_envase * line.cant_envases * line.num_bultos)
            rec.total_peso_envase = sum(sum_list)

    def export_pdf(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        tipos = 1 if self.product_id.as_type_product == 'MP' else 0

        datas['model'] = 'as.wizard.formulas'
        datas['form'] = self.read()[0]
        diccionario = []
        oum_obj = self.env['uom.uom'].search([]).filtered(
            lambda uo: uo.category_id.id == self.product_uom_id.category_id.id and uo.uom_type == "reference")

        file_like_object = BytesIO()
        EAN = barcode.get_barcode_class('code128')
        ean = EAN(self.as_barcode_mpp_1_CDB(), writer=ImageWriter())
        ean.write(file_like_object, options={"write_text": False})
        self.as_imge = base64.b64encode(file_like_object.getvalue())

        for idx, line in enumerate(self.quimetal_lines_ids):
            for item in range(0, line.num_bultos):
                diccionario.append({
                    'cant': line.cant_envases,
                    'weight': line.peso_envase * line.cant_envases,
                    'uom_reference': oum_obj.name,
                })

        datas = {
            'data': diccionario,
        }

        pdf = None
        if tipos == 1:
            pdf = self.env.ref('stock_barcode_quimetal.as_reportes_etiquetas_mp')._render_qweb_pdf([self.id],
                                                                                                   data=datas)
        else:
            pdf = self.env.ref('stock_barcode_quimetal.as_reportes_etiquetas_pp')._render_qweb_pdf([self.id],
                                                                                                   data=datas)

        if pdf:
            b64_pdf = base64.b64encode(pdf[0])
            content_bytes = base64.b64decode(b64_pdf, validate=True)
            dt_string = datetime.now().strftime("%d-%m-%Y %H:%M:%S").split(' ')
            filename = f"{self.lot_id.display_name}-{self.product_id.default_code}-{dt_string[0]}-{dt_string[1]}.pdf"
            self.env['google.drive.config'].sudo().upload_pdf(filename, content_bytes)
