# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today  ITAAS (<http://www.itaas.co.th/>).
{
    "name": "Product Stock Forecast Incoming and Outgoing",
    "category": 'Stock',
    'version': '13.0.1.0',
    'summary': 'Stock Inventory Extended.',
    "description": """
        .
    """,
    "sequence": 1,
    "author": "IT as a Service Co., Ltd.",
    "website": "http://www.itaas.co.th/",
    "version": '13.0.1',
    "depends": ['stock'],
    "data": [

        'views/product_template_view.xml',

    ],
    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}