# -*- coding: utf-8 -*-

# Part of ITAAS (www.itaas.co.th)

{
    'name' : 'Itaas Close Create Standard',
    'version' : '13.0.2.0',
    'price' : 'Free',
    'currency': 'THB',
    'category': 'Itaas Close Create Standard',
    'summary' : 'Itaas Close Create Standard',
    'description': """
                Itaas Close Create Standard:
Tags: 
Stock report
            """,
    'author' : 'IT as a Service Co., Ltd.',
    'website' : 'www.itaas.co.th',
    'depends' : ['base','account','sale','sale_management','sales_team','purchase','stock','product'],

    'data' : [
        'views/product_template.xml',
        'views/stock_picking.xml',
        'views/account_move.xml',
        'views/account_payment.xml',
        'views/sale_order.xml',
        'views/purchase_order.xml',
    ],


    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
