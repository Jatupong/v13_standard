# Copyright 2020 ITAAS info@itaas.co.th


{
    "name": "Assign Done qty on Stock Move same with Initial Demand",
    "version": "13.0.1.0.0",
    "category": "Sales Management",
    "author": "ITAAS",
    "website": "https://itaas.co.th",
    "license": "AGPL-3",
    "depends": [
        'stock',
    ],

    "data": [
        'views/stock_picking_view.xml',
        'wizard/picking_multi_assign_qty_views.xml',
    ],
    'installable': True,
}
