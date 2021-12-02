from odoo import http, _
from odoo.http import request
from odoo.modules.module import get_resource_path
from odoo.tools import pdf
import json


class StockBarcodeQuimetalController(http.Controller):

    @http.route('/stock_barcode/print_etiquetas', type='http', auth="user", website=True)
    def print_etiquetas(self, page=0, category=None, topic=None, search='', ppg=False, **post):
        print(post)
        print(123456789)
        return request.render("stoc_barcode_quimetal.create_etiquitas_form", {})
