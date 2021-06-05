# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Book)

{
    'name': 'Quotations Combine Order',
    'version': '13.0.1',
    'category': 'Sales',
    'author': 'ITAAS',
    'sequence': 0.00,
    'summary': 'Quotations Combine Order',
    'description': """
Manage sales quotations combine order.
    """,
    'author': 'ITAAS',
    'website': 'www.itaas.co.th',
    'license': 'LGPL-3',
    'support': 'info@itaas.co.th',
    'depends': ['base_setup','sale','itaas_discount_ontop'],
    'data': [
        'views/sale_order_view.xml',
        'wizard/quotation_combine_wizard.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,

}
