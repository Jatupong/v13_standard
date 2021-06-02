# -*- coding: utf-8 -*-

# Part of ITAAS (www.itaas.co.th)

{
    'name' : 'Print Service Worksheet Report',
    'version': '13.0.0.7',
    'price' : 'Free',
    'currency': 'THB',
    'category': 'Field Service',
    'summary' : 'Print Worksheet Report',
    'description': """
                Worksheet Report:
                    - Creating Service Worksheet Report
Tags: 
Stock report
            """,
    'author' : 'IT as a Service Co., Ltd.',
    'website' : 'www.itaas.co.th',
    'depends' : ['project','pad_project','industry_fsm'],
    'data' : [
        'report/report_reg.xml',
        'report/wortsheet_report.xml',
        'views/woeksheet_view.xml',

    ],
    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
