# -*- coding: utf-8 -*-
{
    'name' : "Ahorasoft EQUIMETAL Barcode",
    'version' : "1.1.8",
    'author'  : "Ahorasoft",
    'description': """
Webservice dummy equimetal
===========================

Custom module for Latproject
    """,
    'category' : "stock",
    'depends' : [
        "web",
        "base",
        "stock",
        "stock_barcode",
        "barcodes",
        "base_gs1_barcode",
        ],
    'website': 'http://www.ahorasoft.com',
    'data' : [
            'security/ir.model.access.csv',
            'views/templates.xml',
            'views/as_barcode_log.xml',
            'views/as_stock_picking.xml',
            'views/stock_picking_views.xml',
             ],
    'demo' : [],
    'qweb': [
        "static/src/xml/as_abstract_client_action.xml",
        "static/src/xml/as_stock_barcode.xml",
    ],  
    'installable': True,
    'application': True,
    'auto_install': False
}
