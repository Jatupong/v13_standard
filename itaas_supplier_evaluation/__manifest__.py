# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Book)
{
    "name": "Itaas Supplier Evaluation",
    "author": "ITAAS",
    "version": "13.0.0.1",
    "category": "Evaluation",
    "website": "www.itaas.co.th",
    "depends": ['stock','purchase',],
    "data": [
        'security/ir.model.access.csv',
        # wizard
        'wizard/stock_evaluation_report_view.xml',
        # view
        'views/stock_evaluation_type_view.xml',
        'views/stock_picking_view.xml',
        'views/res_partner_view.xml',
        # 'views/purchase_order_view.xml',
        'views/stock_evaluation_view.xml',
        'views/stock_evaluation_report_view.xml',
        # report
        'report/report_reg.xml',
        'report/assessment_result_report.xml',
        'report/stock_evaluation_report.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
