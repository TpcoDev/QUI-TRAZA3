import uuid
import yaml
import requests
import json

from odoo import http
from odoo.http import request


class AsWebserviceController(http.Controller):

    @http.route('/tpco/odoo/ws017', auth="public", type="json", method=['POST'], csrf=False)
    def WS017(self, **post):
        post = json.loads(request.httprequest.data)
        res = {}
        as_token = uuid.uuid4().hex
        mensaje_error = {
            "Token": as_token,
            "RespCode": -1,
            "RespMessage": "Error de conexión"
        }
        mensaje_correcto = {
            "jsonrpc": "2.0",
            "id": post['id'],
            "result": {
                "Token": as_token,
                "RespCode": 0,
                "RespMessage": "Producto se agregó correctamente"
            }
        }

        try:
            myapikey = request.httprequest.headers.get("Authorization")
            if not myapikey:
                # self.create_message_log("ws016", as_token, post, 'RECHAZADO', 'API KEY no existe')
                return mensaje_error
            user_id = request.env["res.users.apikeys"]._check_credentials(scope="rpc", key=myapikey)
            request.uid = user_id
            if user_id:
                res['token'] = as_token
                uid = user_id

                # request.session.logout()
                # estructura = self.get_file('ws016.json')
                # es_valido = self.validar_json(post, esquema=estructura)
                # es_valido = True
                uomID = request.env['uom.uom'].sudo().search([
                    ('unidad_sap', '=', post['params']['uomId'])], limit=1)
                if not uomID:
                    uomID = request.env['uom.uom'].sudo().create({
                        'name': f"{post['params']['itemDescription']} ({post['params']['uomId']}) {post['params']['contenidoEnvase']}",
                        'as_contenido_envase': post['params']['contenidoEnvase'],
                        'unidad_sap': post['params']['uomId'],
                        'category_id': 2 if post['params']['unidadReferencia'] == 'KG' else 5,
                        'factor': (1 / post['params']['contenidoEnvase']) if post['params'][
                                                                                 'contenidoEnvase'] > 0 else 1,
                        'uom_type': 'bigger' if post['params']['contenidoEnvase'] > 1 else 'smaller'
                    })

                uomPOID = request.env['uom.uom'].sudo().search([('unidad_sap', '=', post['params']['uomPoId'])],
                                                               limit=1)
                if not uomPOID:
                    uomPOID = request.env['uom.uom'].sudo().create({
                        'name': f"{post['params']['itemDescription']} ({post['params']['uomId']}) {post['params']['contenidoEnvase']}",
                        'as_contenido_envase': post['params']['contenidoEnvase'],
                        'unidad_sap': post['params']['uomId'],
                        'category_id': 2 if post['params']['unidadReferencia'] == 'KG' else 5,
                        'factor': (1 / post['params']['contenidoEnvase']) if post['params'][
                                                                                 'contenidoEnvase'] > 0 else 1,
                        'uom_type': 'bigger' if post['params']['contenidoEnvase'] > 1 else 'smaller'
                    })

                envases_id = request.env['quimetal.envases'].sudo().search(
                    [('cod_envase', '=', post['params']['envase'])], limit=1)

                if not envases_id:
                    envases_id = request.env['quimetal.envases'].sudo().create({
                        'name': post['params']['glosaEnvase'],
                        'cod_envase': post['params']['envase']
                    })

                embalaje_id = request.env['quimetal.embalaje'].sudo().search(
                    [('cod_embalaje', '=', post['params']['embalaje'])], limit=1)
                unid_logistica_id = request.env['quimetal.unid.logisticas'].sudo().search(
                    [('name', '=', post['params']['formatoUnidadLogistica'])], limit=1)
                categ_id = request.env['product.category'].sudo().search(
                    [('id', '=', post['params']['categ_id'])], limit=1)

                vals = {
                    'default_code': post['params']['itemCode'],
                    'name': post['params']['itemDescription'],
                    'type': post['params']['tipoProducto'],
                    'as_type_product': post['params']['tipoProdQuimetal'],
                    'barcode': post['params']['barcode'],
                    'as_contenido_envase': post['params']['contenidoEnvase'],
                    'as_cantidad_envase': post['params']['cantidadEnvase'],
                    'as_cantidad_unidades': post['params']['cantidadUnidades'],
                    'expiration_time': post['params']['expirationTime'],
                    'list_price': 1.00,
                    'taxes_id': [(4, request.env.ref('l10n_cl.ITAX_19').id)],
                    'standard_price': 0.0,
                    'use_expiration_date': True,
                    'tracking': 'lot',
                    'purchase_ok': True,
                    'sale_ok': True,
                    'categ_id': categ_id.id if categ_id else 1,
                    'uom_id': uomID.id if uomID else False,
                    'uom_po_id': uomPOID.id if uomPOID else False,
                    'envase_id': envases_id.id if envases_id else False,
                    'embalaje_id': embalaje_id.id if embalaje_id else False,
                    'unidad_logistica_id': unid_logistica_id.id if unid_logistica_id else False,
                }

                product_id = request.env['product.template'].sudo().search([('id', '=', post['id'])], limit=1)
                if product_id:
                    sale_line = request.env['sale.order.line'].search([('product_id', '=', product_id.id)])
                    purchase_line = request.env['purchase.order.line'].search([('product_id', '=', product_id.id)])
                    stock_line = request.env['stock.move.line'].search([('product_id', '=', product_id.id)])

                    if not sale_line and not purchase_line and not stock_line:
                        product_id.write(vals)
                        mensaje_correcto['result']['RespMessage'] = 'Producto se actualizó'
                    mensaje_correcto['result']['RespMessage'] = 'Producto no se actualizó, porque se han hecho trasacciones'
                    return mensaje_correcto
                else:
                    product_id = request.env['product.template'].sudo().create(vals)
                    return mensaje_correcto

                # uid = request.env.user.id
        except Exception as e:
            # self.create_message_log("ws016", as_token, post, 'RECHAZADO', str(e))
            return mensaje_error

    # def create_message_log(self, method, token, json, state, as_motivo):
    #     val_message = {
    #         "name": method,
    #         "as_token": token,
    #         "as_fecha": datetime.now(),
    #         "as_json": json,
    #         "state": state,
    #         "as_motivo": as_motivo,
    #     }
    # request.env['as.webservice.logs'].sudo().create(val_message)
