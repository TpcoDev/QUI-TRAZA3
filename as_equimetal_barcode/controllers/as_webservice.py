# -*- coding: utf-8 -*-
from odoo.tools.translate import _
import json
import sys
import uuid
from odoo import http
from odoo.http import request, Response
import json
import logging
_logger = logging.getLogger(__name__)
from datetime import timedelta, datetime, date


class as_barcode_quimetal(http.Controller):

    @http.route(['/quimetal/barcode'], auth="public", type="http",csrf=False)
    def barcode(self, **post):
        # order_reference = row_id
        barcode = post.get('barcode') or None
        create_lot = post.get('create') or None

        # barcode = barcode.replace("|","\x1d")
        # barcode = '10455\x1d91MPFIL093\x1d3721\x1d310000031517210308'
        result = ""
        try:
            
            result =  request.env['gs1_barcode'].sudo().decode(barcode)
            # result = biip.parse(barcode,separator_chars=('\x1d'))
            # lote = result.gs1_message.get(ai="10").value
            # product_code = result.gs1_message.get(ai="91").value
            product_code = ''
            product_gtin = ''
            expiration_date = ''
            create_date = ''
            lote = result['10']
            if '91' in result:
                product_code = result['91']
            if '01' in result:
                product_gtin = result['01']
            if '02' in result:
                product_gtin = result['02']
            if '11' in result:
                create_date = result['11']
            if '17' in result:
                expiration_date = result['17']


            product_id = request.env['product.product'].sudo().search(['|',('default_code','=',product_code),('barcode','=',product_gtin)],limit=1)
            if not product_id:
                vals2={
                    'type':True,
                    'lote': lote,
                    'barcode': barcode,
                    'product': False,
                    'gtin': False,
                    'result': json.dumps(result),
                    'existe': True,
                    'product_type': product_id.as_type_product,
                }
            else:
                lot_id = request.env['stock.production.lot'].sudo().search([('name','=',lote),('product_id','=',product_id.id)],limit=1)
                if lot_id:
                    vals2={
                        'type':True,
                        'lote': lote,
                        'barcode': barcode,
                        'product': product_code or product_gtin,
                        'gtin': product_id.barcode,
                        'result': json.dumps(result),
                        'existe': True,
                        'product_type': product_id.as_type_product,
                    }
                    lot_id.message_post(body = barcode)
                else:
                    if not create_lot:
                        vals2={
                            'type':True,
                            'lote': lote,
                            'barcode': barcode,
                            'product': product_code or product_gtin,
                            'gtin': product_id.barcode,
                            'result': json.dumps(result),
                            'existe': False,
                            'product_type': product_id.as_type_product,
                        }
                    else:
                        lot_id = request.env['stock.production.lot'].sudo().create({
                                'product_id': product_id.id,
                                'name': lote,
                                'company_id': request.env.user.company_id.id,
                            })
                        if create_date:
                            request.env.cr.execute("UPDATE stock_production_lot SET create_date = %s WHERE id = %s", (create_date+' 04:00',lot_id.id))
                        if expiration_date:
                            lot_id.expiration_date = expiration_date+' 04:00'

                        vals2={
                            'type':True,
                            'lote': lot_id.name,
                            'barcode': barcode,
                            'product': product_code or product_gtin,
                            'gtin': product_id.barcode,
                            'result': json.dumps(result),
                            'product_type': product_id.as_type_product,
                        }      
                        lot_id.message_post(body = barcode)     
        except Exception as e:
            vals2={
                'type':False,
                'barcode': barcode,
                'result': json.dumps(result),
                'existe': False,
            
            }
        log_id = request.env['as.barcode.log'].sudo().create({
                            'name': barcode,
                            'as_json':json.dumps(vals2),
                    })
        # print (result.gs1_message)
        return json.dumps(vals2)

