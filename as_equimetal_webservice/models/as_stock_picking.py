# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.http import request
import requests, json
from odoo.tests.common import Form
from odoo.exceptions import UserError

address_webservice = {
    'WS005': '/tpco/odoo/ws005',
    'WS004': '/tpco/odoo/ws004',
    'WS006': '/tpco/odoo/ws006',
    'WS099': '/tpco/odoo/ws099',
    'WS018': '/tpco/odoo/ws018',
    'WS021': '/tpco/odoo/ws021',
}


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    uom_orig_id = fields.Char()


class AsStockMove(models.Model):
    _inherit = 'stock.move'

    qtyOrigin = fields.Float(compute='_compute_qty_done')

    @api.depends('move_line_ids.qty_done')
    def _compute_qty_done(self):
        for rec in self:
            rec.qtyOrigin = sum([line.qty_done for line in rec.move_line_ids])


class AsStockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    qty_done_base = fields.Float(compute='_compute_qty_done_base')

    def _compute_qty_done_base(self):
        for rec in self:
            rec.qty_done_base = rec.qty_done / rec.product_uom_id.factor


class AsStockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    opdevtype = fields.Selection(
        selection=[('21', 'Devolución de proveedores'), ('16', 'Devolución de clientes')],
        string='Tipo de Operación'
    )


class AsStockPicking(models.Model):
    _inherit = 'stock.picking'

    as_enviado_sap = fields.Boolean(string='Enviado a SAP')
    as_webservice = fields.Selection(
        [
            ('WS005', 'WS005'),
            ('WS004', 'WS004'),
            ('WS006', 'WS006'),
            ('WS099', 'WS099'),
            ('WS013', 'WS013'),
            ('WS017', 'WS017'),
            ('WS018', 'WS018'),
            ('WS021', 'WS021'),
        ],
        string="Webservice",
    )
    as_ot_num = fields.Integer(string='Numero Documento')
    as_ot_sap = fields.Integer(string='OT SAP')
    as_num_factura = fields.Char(string='Num de Factura')
    as_guia_sap = fields.Char(string='Guía SAP')
    opdevtype = fields.Integer()
    num_fact_prov = fields.Char()
    num_guia_prov = fields.Char()
    f_closed = fields.Integer(related='purchase_id.f_closed', store=True)

    def button_validate(self):
        res = super().button_validate()
        self.validate_webservice()
        return res

    def validate_webservice(self):
        if self.state == 'done':
            if self.picking_type_id.as_rest_factura and not self.as_num_factura and not self.as_guia_sap:
                raise UserError('El Num de Factura y Guía SAP no puede estar vacio')
            self.date_done = fields.Datetime.now()
            self.env.cr.commit()
            if self.picking_type_id.as_webservice:
                self.action_picking_sap()
            if self.location_id.as_webservice and not self.picking_type_id.as_webservice:
                self.action_picking_sap()
            if self.picking_type_id.as_send_automatic:
                self.as_send_email()
            if self.location_id.as_send_automatic and not self.picking_type_id.as_send_automatic:
                self.as_send_email()
        return True

    def as_send_email(self):
        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        self.ensure_one()
        template_id = self._find_mail_template_send()
        lang = self.env.context.get('lang')
        template = self.env['mail.template'].browse(template_id)
        if template.lang:
            lang = template._render_lang(self.ids)[self.id]
        ctx = {
            'default_model': 'stock.picking',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'custom_layout': "mail.mail_notification_paynow",
            'force_email': True,
        }
        wiz = {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

        wiz = Form(self.env['mail.compose.message'].with_context(ctx)).save()
        wiz.action_send_mail()
        self.message_post(body="<b style='color:green;'>Enviado correo</b>")

    def _find_mail_template_send(self, force_confirmation_template=False):
        if self.location_id.as_plantilla == '1':
            template_id = self.env['ir.model.data'].xmlid_to_res_id('as_stock_equimetal.stock_picking_mail_templateD',
                                                                    raise_if_not_found=False)
        else:
            template_id = self.env['ir.model.data'].xmlid_to_res_id('as_stock_equimetal.stock_picking_mail_templateO',
                                                                    raise_if_not_found=False)

        return template_id

    def action_picking_sap(self):
        if self.as_webservice:
            webservice = self.as_webservice
        else:
            if self.picking_type_id.as_webservice:
                webservice = self.picking_type_id.as_webservice
            else:
                webservice = self.location_id.as_webservice
        if webservice:
            if webservice != 'WS005':
                try:
                    token = self.as_get_apikey(self.env.user.id)
                    if token != None:
                        headerVal = {}
                        # headerVal = {'Authorization': token}
                        requestBody = {
                            'res_id': self.name,
                            'mode': False,
                        }
                        credentials = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                        URL = credentials + address_webservice[webservice]
                        r = requests.post(URL, json=requestBody, headers=headerVal)
                        if r.ok:
                            text = r.text
                            info = json.loads(text)
                            if info['result']['RespCode'] == 0:
                                body = "<b style='color:green'>EXITOSO (" + webservice + ")!: </b><br>"
                                body += '<b>' + info['result']['RespMessage'] + '</b>'
                            else:
                                body = "<b style='color:red'>ERROR (" + webservice + ")!: </b><br>"
                                body += '<b>' + info['result']['RespMessage'] + '</b>'
                        else:
                            body = "<b style='color:red'>ERROR (" + webservice + ")!:</b><br> <b> No aceptado por SAP</b><br>"
                    else:
                        body = "<b style='color:red'>ERROR (" + webservice + ")!: </b><br> <b>El Token no encontrado!</b>"
                except Exception as e:
                    body = "<b style='color:red'>ERROR (" + webservice + ")!: </b><b>" + str(e) + "</b><br>"
                self.message_post(body=body)
            if webservice == 'WS005':
                other_loc = False
                other_loc_aprobe = False
                for move_stock in self.move_line_ids_without_package:
                    if move_stock.location_dest_id.as_stock_fail == True:
                        other_loc = True
                    if move_stock.location_dest_id.as_stock_fail == False:
                        other_loc_aprobe = True
                if other_loc:
                    try:
                        token = self.as_get_apikey(self.env.user.id)
                        if token != None:
                            headerVal = {}
                            # headerVal = {'Authorization': token}
                            requestBody = {
                                'res_id': self.name,
                                'mode': True,
                            }
                            credentials = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                            URL = credentials + address_webservice[webservice]
                            r = requests.post(URL, json=requestBody, headers=headerVal)
                            if r.ok:
                                text = r.text
                                info = json.loads(text)
                                if info['result']['RespCode'] == 0:
                                    body = "<b style='color:green'>EXITOSO (" + webservice + ")!: </b><br>"
                                    body += '<b>' + info['result']['RespMessage'] + '</b>'
                                else:
                                    body = "<b style='color:red'>ERROR (" + webservice + ")!: </b><br>"
                                    body += '<b>' + info['result']['RespMessage'] + '</b>'
                            else:
                                body = "<b style='color:red'>ERROR (" + webservice + ")!:</b><br> <b> No aceptado por SAP</b><br>"
                        else:
                            body = "<b style='color:red'>ERROR (" + webservice + ")!: </b><br> <b>El Token no encontrado!</b>"
                    except Exception as e:
                        body = "<b style='color:red'>ERROR (" + webservice + ")!: </b><b>" + str(e) + "</b><br>"

                    self.message_post(body=body)
                    self.message_post(body='<b style="color:blue;">Llamada a Producto Rechazados</b><br/>')
                if other_loc_aprobe:
                    try:
                        token = self.as_get_apikey(self.env.user.id)
                        if token != None:
                            headerVal = {}
                            # headerVal = {'Authorization': token}
                            requestBody = {
                                'res_id': self.name,
                                'mode': False,
                            }
                            credentials = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                            URL = credentials + address_webservice[webservice]
                            r = requests.post(URL, json=requestBody, headers=headerVal)
                            if r.ok:
                                text = r.text
                                info = json.loads(text)
                                if info['result']['RespCode'] == 0:
                                    body = "<b style='color:green'>EXITOSO (" + webservice + ")!: </b><br>"
                                    body += '<b>' + info['result']['RespMessage'] + '</b>'
                                else:
                                    body = "<b style='color:red'>ERROR (" + webservice + ")!: </b><br>"
                                    body += '<b>' + info['result']['RespMessage'] + '</b>'
                            else:
                                body = "<b style='color:red'>ERROR (" + webservice + ")!:</b><br> <b> No aceptado por SAP</b><br>"
                        else:
                            body = "<b style='color:red'>ERROR (" + webservice + ")!: </b><br> <b>El Token no encontrado!</b>"
                    except Exception as e:
                        body = "<b style='color:red'>ERROR (" + webservice + ")!: </b><b>" + str(e) + "</b><br>"
                    self.message_post(body=body)
                    self.message_post(body='<b style="color:blue;">Llamada a Producto Acaptados</b><br/>')

    def as_get_apikey(self, user_id):
        query = self.env.cr.execute("""select key from res_users_apikeys where user_id =""" + str(user_id) + """""")
        result = self.env.cr.fetchall()
        return result[0][0]

    def as_assemble_picking_json(self, webservice):
        picking_line = []
        vals_picking_line = {}
        cont_errores = 0
        for picking in self:
            errores = '<b style="color:orange;">Errores de formulario:</b><br/>'
            # try:
            #     int(picking.name)
            # except Exception as e:
            #     errores+= '<b>* El nombre-docNum no puede tener letras solo Numeros</b><br/>'
            #     cont_errores +=1
            # se ensamblan los stock.move
            for move_stock in picking.move_ids_without_package:
                move = []
                vals_move_line = {}
                for move_line in move_stock.move_line_ids:
                    if not move_line.lot_id:
                        errores += '<b>* Producto No posee Lote</b><br/>'
                        cont_errores += 1
                    vals_move_line = {
                        "distNumber": move_line.lot_id.name,
                        "quantity": move_line.qty_done_base,
                        "quantityOrig": move_line.qty_done,
                        "dateProduction": str(move_line.lot_id.create_date.strftime('%Y-%m-%dT%H:%M:%S')),
                    }
                    if move_line.lot_id.expiration_date:
                        vals_move_line['dateExpiration'] = str(
                            move_line.lot_id.expiration_date.strftime('%Y-%m-%dT%H:%M:%S'))
                    else:
                        vals_move_line['dateExpiration'] = ''
                    move.append(vals_move_line)
                if not move_stock.product_id.default_code:
                    errores += '<b>* Producto No posee Referencia interna</b><br/>'
                    cont_errores += 1
                vals_picking_line = {
                    "itemCode": move_stock.product_id.default_code,
                    "itemDescription": move_stock.product_id.name,
                    "quantity": move_stock.quantity_done,
                    "measureUnit": move_stock.product_uom.name,
                    "quantityOrig": move_stock.qtyOrigin,
                    "measureUnitOrig": move_stock.product_id.uom_org_id,
                    "lote": move,
                }
                picking_line.append(vals_picking_line)
            if webservice == 'WS005':
                try:
                    int(picking.origin)
                except Exception as e:
                    errores += '<b>* El origen-docNumSAP no puede tener letras solo Numeros</b><br/>'
                    cont_errores += 1
                if not picking.partner_id:
                    errores += '<b>* Cliente No seleccionado</b><br/>'
                    cont_errores += 1
                if not picking.origin:
                    errores += '<b>* Campo Origen No completado</b><br/>'
                    cont_errores += 1
                if not picking.date_done:
                    errores += '<b>* Campo Fecha Confirmacion No completado</b><br/>'
                    cont_errores += 1
                if cont_errores <= 0:
                    vals_picking = {
                        "docNum": str(picking.name),
                        "docDate": str(picking.date_done.strftime('%Y-%m-%dT%H:%M:%S') or None),
                        "docNumSAP": picking.origin.split('-')[0],
                        "numFactProv": picking.num_fact_prov,
                        "warehouseCodeOrigin": picking.location_id.name,
                        "warehouseCodeDestination": picking.location_dest_id.name,
                        "cardCode": picking.partner_id.vat,
                        "cardName": picking.partner_id.name,
                        "detalle": picking_line,
                    }
            elif webservice in ('WS004'):
                ubicacion_origen = picking.location_id.name
                if ubicacion_origen == 'Production':
                    ubicacion_origen = 'TRLA'
                if not picking.as_ot_sap:
                    errores += '<b>* OT SAP No completado</b><br/>'
                    cont_errores += 1
                if not picking.date_done:
                    errores += '<b>* Campo Fecha Confirmacion No completado</b><br/>'
                    cont_errores += 1
                if cont_errores <= 0:
                    vals_picking = {
                        "docNum": str(picking.name),
                        "docNumSAP": str(picking.as_ot_sap),
                        "docDate": str(picking.date_done.strftime('%Y-%m-%dT%H:%M:%S') or None),
                        "warehouseCodeOrigin": ubicacion_origen,
                        "warehouseCodeDestination": picking.location_dest_id.name,
                        "detalle": picking_line,
                    }
            elif webservice in ('WS006'):
                if not picking.date_done:
                    errores += '<b>* Campo Fecha Confirmacion No completado</b><br/>'
                    cont_errores += 1
                if cont_errores <= 0:
                    vals_picking = {
                        "docNum": str(picking.name),
                        "docNumSAP": str(picking.as_ot_sap),
                        "docDate": str(picking.date_done.strftime('%Y-%m-%dT%H:%M:%S') or None),
                        "warehouseCodeOrigin": picking.location_id.name,
                        "warehouseCodeDestination": picking.location_dest_id.name,
                        "detalle": picking_line,
                    }
            elif webservice in ('WS099'):
                ubicacion_origen = picking.location_id.name
                if ubicacion_origen == 'Production':
                    ubicacion_origen = 'TRLA'
                if not picking.date_done:
                    errores += '<b>* Campo Fecha Confirmacion No completado</b><br/>'
                    cont_errores += 1
                if cont_errores <= 0:
                    vals_picking = {
                        "docNum": str(picking.name),
                        "docNumSAP": str(picking.as_ot_sap),
                        "docDate": str(picking.date_done.strftime('%Y-%m-%dT%H:%M:%S') or None),
                        "warehouseCodeOrigin": ubicacion_origen,
                        "warehouseCodeDestination": picking.location_dest_id.name,
                        "detalle": picking_line,
                    }
            elif webservice in ('WS018'):
                if not picking.partner_id:
                    errores += '<b>* Cliente No seleccionado</b><br/>'
                    cont_errores += 1
                # if not picking.as_num_factura:
                #     errores+= '<b>* Numero de Factura no completado</b><br/>'
                #     cont_errores +=1
                # if not picking.as_guia_sap:
                #     errores+= '<b>* Numero de guia de despacho no completado</b><br/>'
                #     cont_errores +=1
                if not picking.origin:
                    errores += '<b>* Origen de movimiento no completado</b><br/>'
                    cont_errores += 1
                if not picking.date_done:
                    errores += '<b>* Campo Fecha Confirmacion No completado</b><br/>'
                    cont_errores += 1
                if cont_errores <= 0:
                    vals_picking = {
                        "docNum": str(picking.name),
                        "DocDueDate": str(picking.date_done.strftime('%Y-%m-%dT%H:%M:%S') or None),
                        "warehouseCodeOrigin": picking.location_id.name,
                        "warehouseCodeDestination": picking.location_dest_id.name,
                        "cardCode": picking.partner_id.vat,
                        "cardName": picking.partner_id.name,
                        "numFactura": str(picking.as_num_factura or ''),
                        "numGuiaDesp": str(picking.as_guia_sap or ''),
                        "numOVAsoc": picking.origin,
                        "detalle": picking_line,
                    }
            elif webservice in ('WS021'):
                # if not picking.as_num_factura:
                #     errores+= '<b>* Numero de Factura no completado</b><br/>'
                #     cont_errores +=1
                # if not picking.as_guia_sap:
                #     errores+= '<b>* Numero de guia de despacho no completado</b><br/>'
                #     cont_errores +=1
                if not picking.date_done:
                    errores += '<b>* Campo Fecha Confirmacion No completado</b><br/>'
                    cont_errores += 1
                if cont_errores <= 0:
                    vals_picking = {
                        "docNum": str(picking.name),
                        "docDate": str(picking.date_done.strftime('%Y-%m-%dT%H:%M:%S') or None),
                        "warehouseCodeDestination": picking.location_dest_id.name,
                        "numFactura": str(picking.as_num_factura or ''),
                        "numGuiaDesp": str(picking.as_guia_sap or ''),
                        "detalle": picking_line,
                    }

            if cont_errores > 0:
                self.message_post(body=errores)
            self.message_post(body=vals_picking)
        return vals_picking

    def as_assemble_picking_json_mode(self, webservice, mode):
        picking_line = []
        vals_picking_line = {}
        cont_errores = 0
        for picking in self:
            location_id = picking.location_id.name
            location_dest_id = picking.location_dest_id.name
            errores = '<b style="color:orange;">Errores de formulario:</b><br/>'
            for move_stock in picking.move_ids_without_package:
                move = []
                vals_move_line = {}
                as_total = 0.0
                for move_line in move_stock.move_line_ids:
                    if move_line.location_dest_id.as_stock_fail == mode:
                        location_id = move_line.location_id.name
                        location_dest_id = move_line.location_dest_id.name
                        if not move_line.lot_id:
                            errores += '<b>* Producto No posee Lote</b><br/>'
                            cont_errores += 1
                        vals_move_line = {
                            "distNumber": move_line.lot_id.name,
                            "quantity": move_line.qty_done_base,
                            "quantityOrig": move_line.qty_done,
                            "dateAdmission": str(move_line.lot_id.create_date.strftime('%Y-%m-%dT%H:%M:%S')),
                        }
                        if move_line.lot_id.expiration_date:
                            vals_move_line['dateExpiration'] = str(
                                move_line.lot_id.expiration_date.strftime('%Y-%m-%dT%H:%M:%S'))
                        else:
                            vals_move_line['dateExpiration'] = ''
                        as_total += move_line.qty_done_base
                        move.append(vals_move_line)
                if move != []:
                    if not move_stock.product_id.default_code:
                        errores += '<b>* Producto No posee Referencia interna</b><br/>'
                        cont_errores += 1
                    vals_picking_line = {
                        "itemCode": move_stock.product_id.default_code,
                        "itemDescription": move_stock.product_id.name,
                        "quantity": as_total,
                        "quantityOrig": move_stock.qtyOrigin,
                        "lineNum": picking.origin.split('-')[1] if len(picking.origin.split('-')) > 1 else '',
                        "measureUnitOrig": '' if not move_stock.product_id.uom_orig_id else move_stock.product_id.uom_orig_id.name,
                        "measureUnit": move_stock.product_uom.name,
                        "lote": move,
                    }
                    picking_line.append(vals_picking_line)
            if webservice == 'WS005':
                if not picking.partner_id:
                    errores += '<b>* Cliente No seleccionado</b><br/>'
                    cont_errores += 1
                if not picking.origin:
                    errores += '<b>* Campo Origen No completado</b><br/>'
                    cont_errores += 1
                if not picking.date_done:
                    errores += '<b>* Campo Fecha Confirmacion No completado</b><br/>'
                    cont_errores += 1
                if cont_errores <= 0:
                    vals_picking = {
                        "docNum": str(picking.name),
                        "docDate": str(picking.date_done.strftime('%Y-%m-%dT%H:%M:%S') or None),
                        "docNumSAP": picking.origin.split('-')[0],
                        "numFactProv": '' if not picking.num_fact_prov else picking.num_fact_prov,
                        "numGuiaProv": '' if not picking.num_guia_prov else picking.num_guia_prov,
                        "warehouseCodeOrigin": location_id,
                        "warehouseCodeDestination": location_dest_id,
                        "cardCode": picking.partner_id.vat,
                        "cardName": picking.partner_id.name,
                        "detalle": picking_line,
                    }
            if cont_errores > 0:
                self.message_post(body=errores)
            self.message_post(body=vals_picking)
        return vals_picking
