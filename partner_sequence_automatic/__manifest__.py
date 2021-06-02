# -*- coding: utf-8 -*-
# module template
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Partner Sequence',
    'version': '13.0.0.1',
    'category': 'Base',
    'license': 'AGPL-3',
    'author': "Odoo Tips",
    'website': 'https://www.facebook.com/OdooTips/',
    'depends': ['base','account',
                ],

    'images': ['images/main_screenshot.png'],
    'data': [
             'data/res_partner_sequence.xml',
             'views/res_partner_view.xml',
             ],
    'installable': True,
    'application': True,
}
