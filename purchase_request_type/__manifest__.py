# -*- coding: utf-8 -*-

# Part of ITAAS (www.itaas.co.th)

{
    'name' : 'Itaas Purchase Request Type',
    'version' : '13.0.1',
    'price' : 'Free',
    'currency': 'THB',
    'category': 'Itaas Purchase Request Type',
    'summary' : 'Itaas Purchase Request Type',
    'description': """
                Itaas Purchase Request Type:
Tags: 
Stock report
            """,
    'author' : 'IT as a Service Co., Ltd.',
    'website' : 'www.itaas.co.th',
    'depends' : ['base','bi_material_purchase_requisitions'],
    'data' : [
        'security/ir.model.access.csv',
        'views/purchase_request_type.xml',
    ],
    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
