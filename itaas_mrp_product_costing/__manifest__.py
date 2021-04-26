# -*- coding: utf-8 -*-
# Copyright (c) Open Value All Rights Reserved

{
'name': 'ITAAS MRP Product Costing',
 'summary': 'MRP Product Costing',
 'version': '13.0.1.0',
 'category': 'Manufacturing',
  "website": 'www.itaas.co.th',
  'author': "ITAAS",
  'support': 'info@itaas.co.th',
  'license': "Other proprietary",
    "depends": [
        'stock_account',
        'purchase',
        'mrp',
        'account',
        'analytic',
        'mrp_workorder',
        'itaas_create_stock_account',
    ],
    "data": [
'views/account_move_line_views.xml',
        'views/mrp_production_views.xml',


    ],
  'application': False,
  'installable': True,
  'auto_install': False,
  'images': ['static/description/banner.png'],
}
