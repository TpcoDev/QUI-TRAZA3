# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import timedelta, datetime, date


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    as_barcode = fields.Binary('Codigo Generado')
    as_imge = fields.Binary(string="barcode")

    def as_get_date_lote(self):
        lote = ''
        if self.lot_name:
            lote = str(self.lot_name)
        else:
            lote = str(self.lot_id.name)
        return lote

    def as_get_date_lote_SC(self):
        lote = ''
        if self.lot_name:
            lote = str(self.lot_name)
        else:
            lote = str(self.lot_id.name)
        return lote

    def as_fecha_vencimiento(self):
        fecha_vencimiento = ''
        for line in self:
            # if line.lot_id.expiration_date:
            #     fecha_vencimiento = (line.lot_id.expiration_date-timedelta(hours=4)).strftime('%y%m%d')
            # if not line.lot_id.expiration_date and line.lot_id.expiration_date:
            if line.lot_id.expiration_date:
                fecha_vencimiento = (line.lot_id.expiration_date - timedelta(hours=4)).strftime('%y%m%d')
        return fecha_vencimiento

    def as_fecha_vencimientostr(self):
        fecha_vencimiento = ''
        for line in self:
            # if line.lot_id.expiration_date:
            #     fecha_vencimiento = (line.lot_id.expiration_date-timedelta(hours=4)).strftime('%y-%m-%d')
            # if not line.lot_id.expiration_date and line.lot_id.expiration_date:
            #     fecha_vencimiento = (line.lot_id.expiration_date-timedelta(hours=4)).strftime('%y-%m-%d')
            if line.lot_id.expiration_date:
                fecha_vencimiento = (line.lot_id.expiration_date - timedelta(hours=4)).strftime('%Y-%m-%d')

    def as_barcode_mpp_1(self):
        fecha_vencimiento = ''
        codigo = ''
        for line in self:
            if line.lot_id.expiration_date:
                fecha_vencimiento = (line.lot_id.expiration_date - timedelta(hours=4)).strftime('%y%m%d')
        # if self.product_id.barcode:
        #     codigo += '(01)'+str(self.product_id.barcode)
        if self.as_get_date_lote():
            codigo += '(10)' + str(self.as_get_date_lote())
        codigo += '(91)' + str(self.product_id.default_code)
        # +'(37)'+str(int(self.product_id.as_cantidad_unidades))
        # if self.as_get_peso_neto():
        #     codigo +='(3101)'+str(int(self.as_get_peso_neto()))
        if fecha_vencimiento:
            codigo += '(17)' + str(fecha_vencimiento)
        return codigo

    def as_barcode_mpp_1_CDB(self):
        fecha_vencimiento = ''
        codigo = ''
        for line in self:
            if line.lot_id.expiration_date:
                fecha_vencimiento = (line.lot_id.expiration_date - timedelta(hours=4)).strftime('%y%m%d')
        # if self.product_id.barcode:
        #     codigo += '01'+str(self.product_id.barcode)+'\x1d'
        if self.as_get_date_lote():
            codigo += '10' + str(self.as_get_date_lote_SC()) + '\x1d'
        codigo += '91' + str(self.product_id.default_code) + '\x1d'
        # +'37'+str(int(self.product_id.as_cantidad_unidades))+'\x1d'
        # if self.as_get_peso_neto():
        #     codigo +='3101'+str(int(self.as_get_peso_neto()))+'\x1d'
        if fecha_vencimiento:
            codigo += '17' + str(fecha_vencimiento)
        return codigo

    def as_barcode_pp_1(self):
        fecha_production = ''
        codigo = ''
        for line in self:
            if line.create_date:
                fecha_production = (line.create_date - timedelta(hours=4)).strftime('%y%m%d')
        if self.as_get_date_lote():
            codigo += '(10)' + str(self.as_get_date_lote())
        codigo += '(91)' + str(self.product_id.default_code)
        # +'(37)'+str(int(self.product_id.as_cantidad_unidades))
        # if self.as_get_peso_neto():
        #     codigo +='(3101)'+str(int(self.as_get_peso_neto()))
        if fecha_production:
            codigo += '(11)' + str(fecha_production)
        return codigo

    def as_barcode_pp_1_CDB(self):
        fecha_production = ''
        codigo = ''
        for line in self:
            if line.create_date:
                fecha_production = (line.create_date - timedelta(hours=4)).strftime('%y%m%d')
        if self.as_get_date_lote():
            codigo += '10' + str(self.as_get_date_lote_SC()) + '\x1d'
        codigo += '91' + str(self.product_id.default_code) + '\x1d'
        # +'37'+str(int(self.product_id.as_cantidad_unidades))+'\x1d'
        # if self.as_get_peso_neto():
        #     codigo +='3101'+str(int(self.as_get_peso_neto()))+'\x1d'
        if fecha_production:
            codigo += '11' + str(fecha_production)
        return codigo

    def as_get_peso_neto(self):
        peso = False
        calculo = self.product_id.as_contenido_envase * self.product_id.as_cantidad_envase * self.product_id.as_cantidad_unidades
        if calculo > 0:
            peso = calculo
        return peso

    def as_get_name_product(self, text):
        tam = len(text)
        if tam > 90:
            return str(text[:90])
        else:
            return text
