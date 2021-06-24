# -*- coding: utf-8 -*-

# Part of ITAAS (www.itaas.co.th)

{
    'name' : 'Itaas Partner Delivery Note',
    'version' : '13.0.2.0',
    'price' : 'Free',
    'currency': 'THB',
    'category': 'delivery',
    'summary' : 'delivery',
    'description': """ 
    """,
    'author' : 'IT as a Service Co., Ltd.',
    'website' : 'www.itaas.co.th',
    'depends' : ['sale','stock',],
    'data' : [
        'views/res_partner_view.xml',
        'views/sale_order_view.xml',
        'views/stock_picking_view.xml',
    ],


    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
