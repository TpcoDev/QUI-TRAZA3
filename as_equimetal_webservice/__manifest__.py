# -*- coding: utf-8 -*-
{
    'name': "Ahorasoft EQUIMETAL customizaciones",
    'version': "1.4.1",
    'author': "Ahorasoft",
    'description': """
Webservice dummy equimetal
===========================

Custom module for Latproject
    """,
    'category': "Sale",
    'depends': [
        "base",
        "purchase",
        "stock",
        "sale_management",
        "as_stock_equimetal",
        "product_expiry",
    ],
    'website': 'http://www.ahorasoft.com',
    'data': [
        # 'data/data.xml',
        'views/assets.xml',
        'security/ir.model.access.csv',
        'views/as_mesage_log.xml',
        'views/as_stock_picking.xml',
        'views/as_res_config.xml',
        'views/as_sale_order.xml',
        'views/stock_picking_views.xml',
        'views/product_views.xml',
        'views/as_modelos.xml',
        'views/as_campos_x.xml',
        'views/as_purchase_order.xml',
        'views/uom.xml'
    ],
    'demo': [],
    'installable': True,
    'auto_install': False
}
