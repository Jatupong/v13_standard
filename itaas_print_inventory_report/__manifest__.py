# -*- coding: utf-8 -*-

# Part of ITAAS (www.itaas.co.th)

{
    'name' : 'Print Stock Picking Report',
    'version' : '13.0.0.1',
    'price' : 'Free',
    'currency': 'THB',
    'category': 'Stock',
    'summary' : 'Print Stock Picking Report',
    'description': """
                Stock Report:
                    - Creating Stock Report
Tags: 
Stock report
            """,
    'author' : 'IT as a Service Co., Ltd.',
    'website' : 'www.itaas.co.th',
    'depends' : ['sale','purchase','base','account','thai_accounting'],
    'data' : [

        'report/product_bill_report.xml',
        'report/product_bill_report02.xml',
        'report/product_bill_report03.xml',
        'report/product_bill_report04.xml',
        'report/product_bill_report05.xml',
        'report/product_bill_report06.xml',
        'report/stock_count_report.xml',

        'wizard/stock_count_wizard_view.xml',
    ],


    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
