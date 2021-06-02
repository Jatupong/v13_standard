# -*- coding: utf-8 -*-
#13.0.1.0 - inital
#13.0.2.0 - add create auto button for make order easier
#13.0.3.0 - more field for start date, start deloivery date, standard qty and more compute for consume qty, remain qty, delivered qty, remain to delivery qty
#         - create auto button will do all order in one time and consider in case some item has been done before another , then other item still continue but over
#         - remain qty will stop order
#         - remove auto job cron since single click will do it
{
    'name': 'Blanket Sale Order',
    'version': '13.0.3.0',
    'sequence': 1,
    'category': 'Sales',
    'description':
        """
        This Module add below functionality into odoo

        1.Blanket Sale Order\n

odoo sale Blanket order
odoo Blanket order
odoo blanket sale order
blanket sale order 
sale blanket order
order blanket in odoo 
order process in blanket 

    """,
    'summary': 'Odoo app allow Blanket Sale Order aggreement between Seller and Customer, sale Blanket order, Blanket order, long term Sale order, Blanket Order',
    'depends': ['sale_management'],
    'data': [
        'data/blanket_sequence_view.xml',
        'views/blanket_order_view.xml',
        'views/sale_view.xml',
        'wizard/create_sale_quotation_view.xml',
        'data/cron_blanket_expiry_view.xml',
        ],
    'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
