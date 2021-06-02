# -*- coding: utf-8 -*-
{
    'name': 'Sale & Invoice Discount',
    'description': 'Manage Discount on Sale Order and Invoice ',
    'summary': '',
    'category': 'Accounting',
    'version': '1.1',
    'website': 'www.itaas.co.th',
    'author': 'ITAAS',
    'depends': ['base', 'account', 'sale','purchase'],
    'data': [
        'invoice_discount/invoice_discount_view.xml',
        'sale_discount/sale_discount_view.xml',
        'purchase_discount/purchase_discount_view.xml',

    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
