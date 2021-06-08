# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Book)
{
    "name": "Itaas sale stock",
    "author": "ITAAS",
    "version": "13.0.0.2",
    "category": "mrp",
    "website": "www.itaas.co.th",
    "depends": ['sale','stock','account','product','sale_stock'],
    "data": [
        'views/sale_order_view.xml',
        'views/stock_picking_view.xml',

    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
