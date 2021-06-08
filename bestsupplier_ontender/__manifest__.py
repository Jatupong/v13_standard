# -*- coding: utf-8 -*-
# Copyright (c) 2015-Present TidyWay Software Solution. (<https://tidyway.in/>)

{
    'name': 'Choose Best Supplier On Tender',
    'version': '1.0',
    'category': 'purchase',
    'summary': 'Choose The Best Supplier At The Best Price',
    'description': """
Choose The Best Supplier At The Best Price
--------------------------------------------------------------------
* Create/Generate Bids,
* Create Quotes For Multiple Suppliers,
* Send Quotes To Suppliers(via email),
* Supplier Edit Its Own Quote's(via portal users),
* Finalize quote, 
* Compare all bid/tender lines then choose best one,
* Confirm best quote Lines,
* Generate Final Purchase Order's.
    """,
    'author': 'TidyWay',
    'website': 'http://www.tidyway.in',
    'depends': ['purchase_requisition'],
    'data': [
             'wizard/generate_purchase_view.xml',
             'wizard/bid_line_qty_view.xml',
             'view/purchase_view.xml',
             ],
    'price': 90,
    'currency': 'EUR',
    'installable': True,
    'license': 'OPL-1',
    'application': True,
    'auto_install': False,
    'images': ['images/tender_1.jpg'],
    'live_test_url': 'https://youtu.be/mUGihrNFtQo'
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
