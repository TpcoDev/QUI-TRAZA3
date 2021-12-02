# -*- coding: utf-8 -*-
from odoo import api, models, fields,_
from odoo.exceptions import UserError
from datetime import datetime
import time
import calendar
from datetime import datetime, timedelta
from time import mktime
import time
from time import mktime
from dateutil.relativedelta import relativedelta

class ReportTax(models.AbstractModel):
    _name = 'report.as_stock_equimetal.as_reportes_etiquetas'


    def _get_report_values(self, docids, data=None):#Parametros del WIZARD
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        # fechaf = datetime.strptime(str(data['form']['end_date']), '%Y-%m-%d').strftime('%d/%m/%Y')
        # fechai = datetime.strptime(str(data['form']['start_date']), '%Y-%m-%d').strftime('%d/%m/%Y')
        return {
            'data': data['form'],
            # 'fechai': fechai,
            # 'fechaf': fechaf,
            'company': self.env.user.company_id,
            # 'usuario': self.get_user(data['form']),
            # 'cliente': self.get_cliente(data['form']),
            # #'sucursal': self.get_sucursal(data['form']),
            'producto': self.env['product.product'].sudo().search([('id', '=',data['form']['wiz_lineas'])]),
            # 'result_clientes': self.result_clientes(data['form']),

        }

    def resultado(self,data):
        consulta_clientes = ("""
            select default_code from product_product
            """) 

        self.env.cr.execute(consulta_clientes)
        clientes = [k for k in self.env.cr.fetchall()]
        return clientes