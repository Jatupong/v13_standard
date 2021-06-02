# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Sales Orders',
    'version': '13.0.1',
    'category': 'Sales',
    'author': 'ITAAS',
    'sequence': 0.00,
    'summary': 'Sales Orders',
    'description': """
Manage sales quotations and orders Multi Confirmation.
    """,
    'author': 'ITAAS',
    'website': 'www.itaas.co.th',
    'license': 'LGPL-3',
    'support': 'info@itaas.co.th',
    'depends': ['sale','web'],
    'data': [
        'views/sale_order_view.xml',
        'views/account_move_view.xml',
        # 'views/external_layout_standard_interit.xml',  ########### REMOVE BY JA due to error on odoo.sh ##17/09/2020
        # 'report/report_saleorder_document_interit.xml', ########### REMOVE BY JA due to error on odoo.sh ##17/09/2020
        'report/report_reg.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,

}
