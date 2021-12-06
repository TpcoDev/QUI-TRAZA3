import base64

from odoo import http, _
from odoo.http import request
from odoo.modules.module import get_resource_path
from odoo.tools import pdf
import json

from io import BytesIO

import barcode
from barcode.writer import ImageWriter


class StockBarcodeQuimetalController(http.Controller):

    @http.route('/stock_barcode_quimetal/print_label', type='json', auth="public", methods=['POST'], website=True,
                csrf=False)
    def print_label(self, **kw):
        user = request.env.user
        response = {}
        if kw.get('id', False):
            id = int(kw.get('id'))
            obj_move_line = request.env['stock.move.line'].sudo().browse(id)
            diccionario = []

            file_like_object = BytesIO()
            EAN = barcode.get_barcode_class('code128')
            ean = EAN(obj_move_line.as_barcode_mpp_1_CDB(), writer=ImageWriter())
            ean.write(file_like_object, options={"write_text": False})
            obj_move_line.as_imge = base64.b64encode(file_like_object.getvalue())

            oum_obj = request.env['uom.uom'].sudo().search([]).filtered(
                lambda
                    uo: uo.category_id.id == obj_move_line.product_uom_id.category_id.id and uo.uom_type == "reference")

            for idx, line in enumerate(obj_move_line.quimetal_lines_ids):
                for item in range(0, line.num_bultos):
                    diccionario.append({
                        'cant': line.cant_envases,
                        'weight': line.peso_envase * line.cant_envases,
                        'uom_reference': oum_obj.name,
                    })

            datas = {
                'data': diccionario,
            }

            if diccionario:
                pdf = request.env.ref('stock_barcode_quimetal.as_reportes_etiquetas_mp').sudo()._render_qweb_pdf([id], data=datas)[0]
                b64_pdf = base64.b64encode(pdf)
                bytes = base64.b64decode(b64_pdf, validate=True)
                response = {
                    'print': True,
                    'bytes': b64_pdf
                }
            else:
                response = {
                    'print': False,
                }

            # pdfhttpheaders = [
            #     ('Content-Type', 'application/pdf'),
            #     ('Content-Length', len(pdf)),
            # ]
            # return request.make_response(pdf, headers=pdfhttpheaders)

        return response
