# Copyright 2020 ITAAS info@itaas.co.th


{
    "name": "Sale Order Type",
    "version": "13.0.2.1",
    "category": "Sales Management",
    "author": "ITAAS",
    "website": "https://itaas.co.th",
    "license": "AGPL-3",
    "depends": [
        'sale_stock',
        'account',
        'sale_management',
    ],
    "demo": [
        "demo/sale_order_demo.xml",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/default_type.xml",
        # "views/res_user_view.xml",
        "views/sale_order_type_view.xml",
        "views/res_partner_view.xml",
        "views/sale_order_view.xml",
    ],
    'installable': True,
}
