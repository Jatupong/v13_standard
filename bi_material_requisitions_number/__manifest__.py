# -*- coding: utf-8 -*-
{
    'name': 'Material Purchase Requisition Line Number',
    'description': 'Add automatic numeration for material purchase requisition lines',
    'version': '13.0.0.1',
    'category': 'requisitions',
    'sequence': 14,
    'summary': '',
    'author': 'ADHOC SA',
    'website': 'www.adhoc.com.ar',
    'license': 'AGPL-3',
    'images': [
    ],
    'depends': [
        'bi_material_purchase_requisitions',
    ],
    'data': [
        'views/material_purchase_requisition_view.xml',
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
