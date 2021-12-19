# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.http import request
import requests, json
from odoo.tests.common import Form
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    f_closed = fields.Integer(default=0)
    oc_state = fields.Selection(
        compute='_compute_oc_state',
        selection=[('open', _('Open')), ('closed', _('Closed'))],
    )

    @api.depends('f_closed')
    def _compute_oc_state(self):
        for record in self:
            if record.f_closed == 1:
                record.oc_state = 'closed'
            else:
                record.oc_state = 'open'

    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        pickings = self.env['stock.picking'].search([('origin', '=', self.name)])
        for pick in pickings:
            pick.partner_id = self.partner_id
        return res
