# -*- coding: utf-8 -*-
# ©  2015-2019 Deltatech
# See README.rst file on addons root folder for license details
{
    'name': "Deltatech Delivery Base",
    'version': '13.0.0.0.0',
    "author": "Terrabit, Dorin Hongu",
    "website": "https://www.terrabit.ro",
    "support": "odoo@terrabit.ro",
    'category': 'Warehouse',

    'depends': ['delivery', 'base_address_city'],
    'data': [
        'views/delivery_view.xml',
        'views/stock_picking_view.xml',
        'wizard/delivery_carrier_details_view.xml',
        'security/ir.model.access.csv'
    ],

    "license": "LGPL-3",
    "images": ['static/description/main_screenshot.png'],

}
