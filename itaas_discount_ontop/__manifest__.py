# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2020. All rights reserved.
{
    'name': 'Itaas Discount Ontop',
    'version': '13.0.2.0',
    'summary': 'Itaas Discount Ontop',
    'sequence': 1,
    'author': 'Itaas Discount Ontop.',
    'description': 'Itaas Discount Ontop',
    'category': 'Itaas Discount Ontop',
    'website': 'http://www.technaureus.com',
    'depends': ['base','sale','account','purchase','crm_opportunity_product'],
    'data': [
        'views/discount_ontop.xml',
        'views/discount_ontop_account.xml',
        'views/discount_ontop_purchase.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
