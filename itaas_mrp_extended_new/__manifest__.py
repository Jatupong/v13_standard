# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev JA)
#13.0.1.0 - 04/06/2021 - Initial
{
    "name": "Itaas Mrp Extended New",
    "author": "ITAAS",
    "version": "13.0.1.0",
    "category": "mrp",
    "website": "www.itaas.co.th",
    "depends": ['mrp','sale','stock','base','product','bi_material_purchase_requisitions','requisition_update'],
    "data": [
        'views/sale_order.xml',
        'views/production_order.xml',


    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
