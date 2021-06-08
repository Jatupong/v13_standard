# -*- coding: utf-8 -*-

# Part of ITAAS (www.itaas.co.th)
{
    'name' : 'Customer To Invoice Billto',
    'version' : '11.0.1',
    'price' : 'Free',
    'currency': 'THB',
    'category': 'Customer To Invoice Billto',
    'summary' : 'Customer To Invoice Billto',
    'description': """
                General Company Setting:
Tags: 
Stock report
            """,
    'author' : 'IT as a Service Co., Ltd.',
    'website' : 'www.itaas.co.th',
    'depends' : ['base','account','thai_accounting'],
    'data' : [
        'views/res_partner_view.xml',
        'views/account_move.xml',
    ],


    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
