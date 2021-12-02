# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, except_orm, ValidationError
import re
import xlrd
from xlrd import open_workbook
import base64
import math
from odoo import tools
import barcode
from barcode.writer import ImageWriter
import logging
from io import BytesIO
import base64
_logger = logging.getLogger(__name__)

class as_wizard_fromulas_stock(models.Model):
    _name="as.wizard.formulas"
    _description="Calculo de etiquetas por formulas"

    wiz_lineas = fields.Many2many('as.wizard.lines', string='Lineas')
    tipo = fields.Char('Tipo')
    modelo = fields.Char('modelo')
    
    def etiquetas(self):
        self.ensure_one()
        context = self._context

    def get_default(self):
        if self.env.context.get("message",False):
            return self.env.context.get("message")
        return False 

    @api.model
    def default_get(self, fields):
        res = super(as_wizard_fromulas_stock, self).default_get(fields)
        res_ids = self._context.get('active_ids')
        as_modelo = self._context.get('active_model')
        self.modelo = self._context.get('active_model')
        as_tipo = self._context.get('tipo')
        self.tipo = self._context.get('tipo')
        dictlinestock = []
        tipo_producto=''
        if as_tipo == 1:
            tipo_producto = 'MP'
        else:
            tipo_producto = 'PP'

        # Si el modelo del contexto es production lot (LOTE)
        if as_modelo == "stock.production.lot":
            if res_ids[0]:
                so_line = res_ids[0]
                so_line_obj = self.env['stock.production.lot'].browse(res_ids)
                promo_list = []
                # Materia Prima
                for move in so_line_obj:
                    datos_producto = move.product_id
                    if move.product_id.as_type_product != tipo_producto:
                        raise UserError(_("El producto debe ser %s") % tipo_producto)
                    calculo = datos_producto.as_contenido_envase * datos_producto.as_cantidad_envase * datos_producto.as_cantidad_unidades
                    kg_compra = move.product_qty
                    if calculo > 0:
                        total = kg_compra/calculo
                    else:
                        total = kg_compra
                    total = math.ceil(total)
                    vasl={
                            'product_id': move.product_id.id,
                            'as_cantidades': total,
                            'lots_id': move.id,
                            'as_done': kg_compra,
                        }
                    dictlinestock.append([0, 0, vasl])
          
        # Si el modelo del contexto es stock picking
        if as_modelo == "stock.picking":
            if res_ids[0]:
                so_line = res_ids[0]
                so_line_obj = self.env['stock.picking'].browse(so_line)
                promo_list = []
                # Materia Prima
                for move in so_line_obj.move_line_ids_without_package:
                    datos_producto = move.product_id
                    if move.product_id.as_type_product != tipo_producto:
                        raise UserError(_("El producto debe ser %s") % tipo_producto)
                    calculo = datos_producto.as_contenido_envase * datos_producto.as_cantidad_envase * datos_producto.as_cantidad_unidades
                    kg_compra = move.qty_done
                    if calculo > 0:
                        total = kg_compra/calculo
                    else:
                        total = kg_compra
                    total = math.ceil(total)
                    vasl={
                            'product_id': move.product_id.id,
                            'operacion_id': move.id,
                            'as_cantidades': total,
                            'lots_id': move.lot_id.id,
                            'as_done': move.qty_done,
                        }
                    dictlinestock.append([0, 0, vasl])

        promos_aprobadas = []
        res.update({
            'wiz_lineas': dictlinestock,
            'tipo': self._context.get('tipo'),
            'modelo':  self._context.get('active_model'),
        })
        return res

    def export_pdf(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        tipos = self._context.get('tipo')
        datas['model'] = 'as.wizard.formulas'
        datas['form'] = self.read()[0]
        diccionario = []
        # tipo 1 move
        if self._context.get('tipo') == 1:
            for contexto_lotes in self.wiz_lineas:
                if self.modelo != "stock.production.lot":
                    file_like_object = BytesIO()
                    EAN = barcode.get_barcode_class('code128')
                    ean = EAN(contexto_lotes.operacion_id.as_barcode_mpp_1_CDB(), writer=ImageWriter())
                    ean.write(file_like_object,options={"write_text": False})
                    contexto_lotes.operacion_id.as_imge = base64.b64encode(file_like_object.getvalue())
                    for i in range (0,contexto_lotes.as_cantidades):
                        diccionario.append(contexto_lotes.operacion_id.id)                    
                else:
                    move_id = self.env['stock.move.line'].search([('lot_id','=',contexto_lotes.lots_id.id)],order='date asc',limit=1)
                    if not move_id:
                        raise UserError("El producto no posee Stock")
                    file_like_object = BytesIO()
                    EAN = barcode.get_barcode_class('code128')
                    ean = EAN(move_id.as_barcode_mpp_1_CDB(), writer=ImageWriter())
                    ean.write(file_like_object,options={"write_text": False})
                    move_id.as_imge = base64.b64encode(file_like_object.getvalue())
                    for i in range (0,contexto_lotes.as_cantidades):
                        diccionario.append(move_id.id)
            if diccionario == []:
                raise UserError("Debe guardar el formulario para generar reporte")
            return self.env.ref('as_stock_equimetal.as_reporte_2').report_action(diccionario)
        else:
            for contexto_lotes in self.wiz_lineas:
                if self.modelo != "stock.production.lot":
                    file_like_object = BytesIO()
                    EAN = barcode.get_barcode_class('code128')
                    ean = EAN(contexto_lotes.operacion_id.as_barcode_pp_1_CDB(), writer=ImageWriter())
                    ean.write(file_like_object,options={"write_text": False})
                    contexto_lotes.operacion_id.as_imge = base64.b64encode(file_like_object.getvalue())

                    for i in range (0,contexto_lotes.as_cantidades):
                        diccionario.append(contexto_lotes.operacion_id.id)                    
                else:
                    move_id = self.env['stock.move.line'].search([('lot_id','=',contexto_lotes.lots_id.id)],order='date asc',limit=1)
                    if not move_id:
                        raise UserError("El producto no posee Stock")
                    file_like_object = BytesIO()
                    EAN = barcode.get_barcode_class('code128')
                    ean = EAN(move_id.as_barcode_pp_1_CDB(), writer=ImageWriter())
                    ean.write(file_like_object,options={"write_text": False})
                    move_id.as_imge = base64.b64encode(file_like_object.getvalue())
                    for i in range (0,contexto_lotes.as_cantidades):
                        diccionario.append(move_id.id)
                    
            if diccionario == []:
                raise UserError("Debe guardar el formulario para generar reporte")
            return self.env.ref('as_stock_equimetal.as_reportes_etiquetas_pdf').report_action(diccionario)

class as_wizard_fromulas_lines(models.Model):
    _name="as.wizard.lines"
    _description="Modelo wizard para lineas"

    product_id = fields.Many2one('product.product', 'Producto')
    operacion_id = fields.Many2one('stock.move.line', 'Movimiento Linea')
    operacion_move_id = fields.Many2one('stock.move', 'Movimiento')
    as_cantidades = fields.Integer(string = 'Cantidades')
    as_done = fields.Integer(string = 'Realizado')
    lots_id = fields.Many2one('stock.production.lot', 'Lote')

#SELF . WIZ LINE