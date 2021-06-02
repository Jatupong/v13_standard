# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today  itaas.co.th

{
    'name' : 'Print Accounting WHT Report',
    'version' : '13.0.1',
    'price' : 'Free',
    'currency': 'THB',
    'category': 'Accounting',
    'summary' : 'Print Accounting Report',
    'description': """
                Accounting Report:
                    - Creating Accounting Report
Tags: 
Stock report
            """,
    'author' : 'IT as a Service Co., Ltd.',
    'website' : 'www.itaas.co.th',
    'depends' : ['account','thai_accounting'],
    'data' : [
        'report/report_reg.xml',
        'report/wht_pnd_2_entries_report.xml',
        'report/wht_pnd_3_entries_report.xml',
        'report/wht_pnd_53_entries_report.xml',
        'report/wht_pnd_item_report.xml',
        'wizard/report_pnd_wizard_view.xml',
        'report/font_pnd2_report.xml',
        'report/font_pnd3_report.xml',
        'report/font_pnd53_report.xml',

    ],


    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
