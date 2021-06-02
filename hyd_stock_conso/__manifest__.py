{
    "name": "Track Stock Move & Quota",
    "summary": """This module help you to track what a unit has """
               """consume during a period and apply a Quota to a unit""",
    "category": "Warehouse",
    "version": "0.1.5",
    "author": "HyD Freelance",
    "support": "mail.hyd.freelance@gmail.com",
    "website": "",
    "license": "LGPL-3",
    "depends": ['stock'],
    "data": [
        # views
        "views/menu.xml",
        "views/consumption_unit_views.xml",
        "views/cons_percent_views.xml",
        "views/stock_picking_views.xml",
        "views/consumption_rule_views.xml",

        # security
        "security/ir.model.access.csv"],
    'demo': [],
    'test': [],
    'installable': True,
    'price': 0,
    'currency': 'EUR',
    'images': ['static/images/main_screenshot.png']
}
