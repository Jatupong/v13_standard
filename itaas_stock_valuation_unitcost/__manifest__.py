# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today  ITAAS (<http://www.itaas.co.th/>).
# fix เรื่อง reverse move ของ V13
{
    "name": "Stock Valuation Unit Price",
    'version': '13.0.1.0',
    "category": 'itaas',
    'summary': 'Stock Valuation Unit Price',
    "description": """
        .
    """,
    "sequence": 1,
    "author": "IT as a Service Co., Ltd.",
    "website": "http://www.itaas.co.th/",
    "version": '1.0',
    "depends": ['base','stock','stock_account'],
    "data": [
        'views/stock_valuation_layer_view.xml',

    ],
    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
