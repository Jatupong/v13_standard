# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Book)

{
    'name': 'Itaas Uom Class',
    'description': """

    """,
    'version': '13.0.2.0',
    'category': 'uom',
    'auto_install': True,
    'depends': ['sale','purchase','bi_material_purchase_requisitions','purchase_request','account'],
    'data': [

        'views/product_template_view.xml',
        'views/sale_view.xml',
        'views/purchase_view.xml',
        'views/requisitions_view.xml',
        'views/purchase_request_view.xml',
        'views/account_view.xml',

    ],
    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}