# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today  ITAAS (<http://www.itaas.co.th/>).
{
    "name": "Itaas Inventory Adjustment Sequence",
    'version': '13.0.1.0',
    "category": 'itaas',
    'summary': 'Inventory Adjustment Sequence.',
    "description": """
        .
    """,
    "sequence": 1,
    "author": "IT as a Service Co., Ltd.",
    "website": "http://www.itaas.co.th/",
    "version": '1.0',
    "depends": ['base','stock'],
    "data": [
        'views/sequence.xml',
        'views/stock_inventory.xml',
    ],
    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
