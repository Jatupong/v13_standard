{
    'name': 'Odoo Missing Transaction Report',
    'version': '13.0.0.0',
    'author': 'Pragmatic TechSoft Pvt Ltd.',
    'website': "www.pragtech.co.in",
    'category': 'Tools',
    'depends': ['sale', 'account'],
    'summary': 'Odoo Missing Transaction Report missing transactions transactions report',
    'description': '''
Odoo Missing Transaction Report
===============================
<keywords>    
missing transactions
transactions report
''',
    'data': [
        'views/sale_order_view.xml',
        'views/account_invoice_view.xml',
        'reports/sale_order_report.xml',
        'reports/account_report.xml',
    ],
    'images': ['static/description/Animated-missing-transaction.gif'],
    'license': 'OPL-1',
    'price': 0,
    'currency': 'EUR',
    'installable': True,
    'auto_install': False,
}
