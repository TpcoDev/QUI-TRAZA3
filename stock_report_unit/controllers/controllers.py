# -*- coding: utf-8 -*-
# from odoo import http


# class Tarea165(http.Controller):
#     @http.route('/tarea_1_6_5/tarea_1_6_5/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tarea_1_6_5/tarea_1_6_5/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tarea_1_6_5.listing', {
#             'root': '/tarea_1_6_5/tarea_1_6_5',
#             'objects': http.request.env['tarea_1_6_5.tarea_1_6_5'].search([]),
#         })

#     @http.route('/tarea_1_6_5/tarea_1_6_5/objects/<model("tarea_1_6_5.tarea_1_6_5"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tarea_1_6_5.object', {
#             'object': obj
#         })
