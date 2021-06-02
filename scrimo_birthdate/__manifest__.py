# -*- coding: utf-8 -*-
# © 2020 SCRIMO GmbH (<http://www.scrimo.com>)
{
    'name': 'SCRIMO Birthdate',
    'summary': "SCRIMO GmbH - Birthdate",
    'version': '1.1.1',
    'author': "SCRIMO GmbH, let IT flow",
    'license': "AGPL-3",
    'maintainer': 'SCRIMO GmbH',
    'category': 'Extra Tools',
    'website': 'http://www.scrimo.com',
    'depends': ['base'],
    'description': """SCRIMO GmbH Birthdate
    
     15.03.2020 - 1.0 Init (Developer: ROWE)
     21.03.2020 - 1.1 include under 18
     24.03.2020 - 1.1.1 - new Filter and Kanbanview
    
    """,
    'data': [
       # 'security/security.xml',
       # 'security/ir.model.access.csv',

       # 'data/data.xml',

       # 'report/#.xml',

       'views/sc_partner_view.xml',

       # 'views/sc_menu.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
}