# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Quotations/Sales Orders Multiple Confirm',
    'version': '13.0.1',
    'category': 'Sales',
    'author': 'ITAAS',
    'sequence': 0.00,
    'summary': 'Quotations/Sales Orders Multiple Confirm',
    'description': """
Manage sales quotations and orders Multi Confirmation.
    """,
    'author': 'ITAAS',
    'website': 'www.itaas.co.th',
    'license': 'LGPL-3',
    'support': 'info@itaas.co.th',
    'depends': ['base_setup','sale'],
    'data': [
        'wizard/sale_make_order_advance_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,

}
