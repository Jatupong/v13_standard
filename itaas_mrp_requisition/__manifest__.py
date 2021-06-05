# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today  ITAAS (<http://www.itaas.co.th/>).
{
    "name": "Requisition Product Reference",
    "category": 'Requisition',
    'author': 'IT as a Service Co., Ltd.',
    'website': 'http://www.itaas.co.th/',
    "version": '13.0.1.0',
    "depends": ['mrp','bi_material_purchase_requisitions'],
    "data": [
        'views/requisition_form.xml',
        'views/stock_move_view.xml',
    ],
    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
