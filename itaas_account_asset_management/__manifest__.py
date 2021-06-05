# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today  ITAAS (<http://www.itaas.co.th/>).
# 13.0.1.0 - first asset for v13
# 13.0.2.0 - update version
{
    "name": "Thailand Asset Management by ITAAS",
    'version': '13.0.2.0',
    "category": 'itaas',
    'summary': 'Asset Management',
    "description": """
        .
    """,
    "sequence": 1,
    "author": "IT as a Service Co., Ltd.",
    "website": "http://www.itaas.co.th/",
    "depends": ['base','account','account_asset','hr'],
    "data": [
        'views/view_account_asset_form.xml',

    ],
    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
