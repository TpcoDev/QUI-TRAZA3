# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.http import request
import requests, json
from odoo.tests.common import Form
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    f_closed = fields.Integer(default=0)

    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        pickings = self.env['stock.picking'].search([('origin', '=', self.name)])
        for pick in pickings:
            pick.partner_id = self.partner_id
        return res
