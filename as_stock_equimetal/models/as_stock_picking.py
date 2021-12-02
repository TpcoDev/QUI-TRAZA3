# -*- coding: utf-8 -*-
from odoo import models, fields, api
import os
from odoo import http
import werkzeug
from werkzeug.urls import url_encode

class StockMoveLine(models.Model):
    _inherit = 'stock.picking'

    partner_id = fields.Many2one(  'res.partner', 'Contact', check_company=True, states={'cancel': [('readonly', True)]})
    as_picking_o = fields.Many2one('stock.picking',string="Movimeinto secundario",compute='_compute_purchase')

    def _compute_purchase(self):
        for line in self:
            if line.id:
                picking = self.env['stock.picking'].search([('origin','=',line.origin),('state','!=','cancel'),('id','!=',line.id)],limit=1)
                line.as_picking_o = picking
            else:
                line.as_picking_o=False

    def _get_share_url(self, redirect=False, signup_partner=False, share_token=None):
        """
        Build the url of the record  that will be sent by mail and adds additional parameters such as
        access_token to bypass the recipient's rights,
        signup_partner to allows the user to create easily an account,
        hash token to allow the user to be authenticated in the chatter of the record portal view, if applicable
        :param redirect : Send the redirect url instead of the direct portal share url
        :param signup_partner: allows the user to create an account with pre-filled fields.
        :param share_token: = partner_id - when given, a hash is generated to allow the user to be authenticated
            in the portal chatter, if any in the target page,
            if the user is redirected to the portal instead of the backend.
        :return: the url of the record with access parameters, if any.
        """
        self.ensure_one()
        params = {
            'model': self._name,
            'res_id': self.id,
        }
        if hasattr(self, 'access_token'):
            params['access_token'] = self._portal_ensure_token()
        if share_token:
            params['share_token'] = share_token
            params['hash'] = self._sign_token(share_token)
        if signup_partner and hasattr(self, 'partner_id') and self.partner_id:
            params.update(self.partner_id.signup_get_auth_param()[self.partner_id.id])

        return '%s?%s' % ('/mail/view' if redirect else self.access_url, url_encode(params))

    def action_picking_send(self):
        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        self.ensure_one()
        template_id = self._find_mail_template()
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
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    def _find_mail_template(self, force_confirmation_template=False):
        if self.location_id.as_plantilla == '1':
            template_id = self.env['ir.model.data'].xmlid_to_res_id('as_stock_equimetal.stock_picking_mail_templateD', raise_if_not_found=False)
        else:
            template_id = self.env['ir.model.data'].xmlid_to_res_id('as_stock_equimetal.stock_picking_mail_templateO', raise_if_not_found=False)

        return template_id