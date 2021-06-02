# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Book)
{
    "name": "Itaas Sale Delivery",
    "author": "ITAAS",
    "version": "13.0.0.1",
    "category": "delivery",
    "website": "www.itaas.co.th",
    "depends": ['sale','delivery','itaas_partner_detail_address'],
    "data": [
        'wizard/choose_delivery_carrier_view.xml',
        'views/delivery_carrier_view.xml',

    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
