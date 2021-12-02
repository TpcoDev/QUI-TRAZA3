# -*- coding: utf-8 -*-
{
    'name': "Stock Barcode Quimetal",
    'summary': "Use barcode scanners to process logistics operations",
    
    'description': """
        
    """,
    'author': "TPCO",
    'website': "http://www.tpco.com",
    'category': 'Inventory/Inventory',
    'version': '1.0',
    'depends': ['stock_barcode'],
    
    # always loaded
    'data': [
        'views/stock_barcode_templates.xml',
        #'views/templates.xml',
    ],

    'qweb': [
        "static/src/xml/qweb_templates.xml",
    ],
}
