# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    f_closed = fields.Integer(default=0)
    oc_state = fields.Selection(
        compute='_compute_oc_state',
        selection=[('open', _('Open')), ('closed', _('Closed'))],
    )
    as_num_comex = fields.Char(string='NUM-COMEX')

    @api.depends('f_closed')
    def _compute_oc_state(self):
        for record in self:
            if record.f_closed == 1:
                record.oc_state = 'closed'
            else:
                record.oc_state = 'open'
