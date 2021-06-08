# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today  ITAAS (<http://www.itaas.co.th/>).
# 13.0.1.0
# feature
#       res.company
# add company field require for thai accounting report
# add company address function (don't use yet)
#       res.partner
# add partner field for branch no and case customer no vat
# add function to unique same customer reference code
#       account.account
# add field to support wht, wht_income,sale_tax_report,purchase_tax_report,cheque, bank_fee(don't use)
#       account.cheque
# add function to create receipt check and payment cheque from payment
# add function to post, cancel, set_to_draft, validate, reject
# add function to post from payment including cheque creation
#      account.journal
# add journal property for adjust for tax
# add journal property for adjust for bank and cheque, bank revese for cheque
# add journal property for debit sequence
# add journal property for tax_invoice sequence
# add journal property for payment sequence
#      account.move
# add field function for invoice and tax invoice process, adjust_move_id
# add field function for invoice and tax invoice process
# add field function for payment with cheque to have detail on account move
# add field function for supplier manual info
# add function action_invoice_generate_tax_invoice()
# add function create_reverse_tax()
# add function roundup()
# add model for account.wht.type
# inherit model for account.move.line for wht_tax,wht_type, wht_reference, amount_before_tax,invoice_date,is_debit with get_is_debit_credit()
# add function for account.move.line roundup(), roundupto()
#      account.payment
# add field for payment, write off account, cheque payment
# add function for cancel
#      account.tax
# add field for wht and tax default property,
#      customer.billing
# for customer billing process without register directly from here
#      account.move
#-----------------------------------------------------------
# 13.0.1.1
# clean view file and remove un-use file
# clean models file and remove un-use file
#-----------------------------------------------------------
# 13.0.1.2
# fix generate or reverse tax for invoice and bill with "generate tax/reverse tax" button
# 13.0.1.3
# add invoice multiple register with deduction
# 13.0.1.4
# change cheque validate sequence number
{
    "name": "Thailand Accounting Enhancement for Odoo Enterprise",
    "category": 'Accounting',
    'summary': 'Thailand Accounting Enhancement.',
    "description": """
        .
    """,
    "sequence": 1,
    "author": "IT as a Service Co., Ltd.",
    "website": "http://www.itaas.co.th/",
    "version": '13.0.1.3',
    "depends": ['account','account_payment','account_asset','account_accountant'],
    "external_dependencies" : {
        'python' : ['bahttext',
                    'num2words',
                    'xlrd'],
    },
    "data": [
        'sequence.xml',
        'views/res_company_view.xml',
        'views/res_partner_view.xml',
        #########################Next View###################
        'views/account_account_view.xml',
        'views/account_journal_view.xml',
        'views/account_tax_view.xml',
        'views/account_move_view.xml',
        'views/account_payment_view.xml',
        'views/customer_billing_view.xml',
        'views/account_cheque_statement_view.xml',

        # data fro preload ###
        'data/account_wht_data.xml',
        # security access and rule
        'security/ir.model.access.csv',


    ],
    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
