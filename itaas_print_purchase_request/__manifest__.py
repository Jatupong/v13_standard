# -*- coding: utf-8 -*-

# Part of ITAAS (www.itaas.co.th)

{
    'name' : 'Print Purchase Request',
    'version' : '13.0.1.0',
    'price' : 'Free',
    'currency': 'THB',
    'category': 'Purchase Request Report',
    'summary' : 'Print Purchase Request Report',
    'description': """
                PR and Purchase Request Report:
Tags: 
Stock report
            """,
    'author' : 'IT as a Service Co., Ltd.',
    'website' : 'www.itaas.co.th',
    'depends' : ['purchase','base','purchase_request'],
    'data' : [

        'report/report_reg.xml',
        'report/purchase_request_report.xml',

    ],


    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
