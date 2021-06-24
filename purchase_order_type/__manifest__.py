# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Book)

{
    "name": "Purchase Order Type",
    "author": "ITAAS",
    "version": "13.0.2.0",
    "category": "mrp",
    "website": "www.itaas.co.th",
    "depends": ['purchase','stock','account','purchase_request'],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "views/purchase_order_type_view.xml",
        "views/res_partner_view.xml",
        "views/res_users_view.xml",
        "views/purchase_order_view.xml",
        "views/purchase_request_view.xml",
        "wizard/purchase_request_line_make_purchase_order_view.xml",

    ],
    'installable': True,
}
