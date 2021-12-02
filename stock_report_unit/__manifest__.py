# -*- coding: utf-8 -*-
{
    'name': "Stock Report Unit",
    'description': """
        Long description of module's purpose
    """,

    'author': "TPCO",
    'website': "http://www.tpco.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0.20211105',

    # any module necessary for this one to work correctly
    'depends': ['stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/stock_quant_inh.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
