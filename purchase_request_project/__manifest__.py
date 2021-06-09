# Copyright 2017-2020 Forgeflow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

{
    "name": "Purchase Request Project",
    "version": "13.0.1.0.0",
    "website": "https://github.com/OCA/purchase-workflow",
    "category": "Purchase Management",
    "depends": ["project", "purchase_request",'analytic'],
    "data": [
        "views/purchase_request_view.xml",
        "views/purchase_order_view.xml",
        "wizard/purchase_request_line_make_purchase_order_view.xml",

    ],
    "license": "LGPL-3",
    "installable": True,
}
