# -*- coding: utf-8 -*-

# Part of ITAAS (www.itaas.co.th)

{
    'name' : 'Print repair Report',
    'version' : '11.0.1',
    'price' : 'Free',
    'currency': 'THB',
    'category': 'repair Report',
    'summary' : 'Print repair Report',
    'description': """
                Quotations and repair Order Report:
Tags: 
Stock report
            """,
    'author' : 'IT as a Service Co., Ltd.',
    'website' : 'www.itaas.co.th',
    'depends' : ['sale','base','itaas_company_setting','repair'],
    'data' : [
        'report/report_reg.xml',
        'report/repair_report.xml',
        'report/project_service_report.xml',
        'report/delivery_repair_report.xml',

        'views/repair_order.xml'
    ],


    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
