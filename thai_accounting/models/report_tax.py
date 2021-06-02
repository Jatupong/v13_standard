# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today (ITAAS)

from odoo import api, fields, models

class report_sale_tax_report(models.AbstractModel):
    _name = 'report.thai_accounting.sale_tax_report_id'

    def get_amount_multi_currency(self,move_id):
        total_amount = 0.0
        tax_amount = 0.0
        for line in move_id.line_ids:
            total_amount += abs(line.debit)
            if line.account_id.sale_tax_report:
                tax_amount += abs(line.balance)
        return total_amount, tax_amount


    @api.model
    def _get_report_values(self, docids, data=None):
    # def get_report_values(self, docids, data=None):

        company_id = self.env.user.company_id
        docs = False
        step = self.env.user.company_id.invoice_step
        # domain = [('type','in',('out_invoice','out_refund')),('tax_inv_generated', '=', True),('tax_inv_no', '!=', False)]

        # print data['form']['tax_id']
        if self.env.user.company_id.invoice_step == '1step':
            domain = [('type', 'in', ('out_invoice', 'out_refund')), ('number', '!=', False), ('state', '!=', 'draft'),('tax_id', '=', data['form']['tax_id'][0])]
            domain.append(('date_invoice', '>=', data['form']['date_from']))
            domain.append(('date_invoice', '<=', data['form']['date_to']))
            docs = self.env['account.invoice'].search(domain, order='date_invoice,number asc')
        else:
            domain = [('type', 'in', ('out_invoice', 'out_refund')), ('tax_inv_generated', '=', True),
                      ('tax_inv_no', '!=', False),('tax_id', '=', data['form']['tax_id'][0])]
            domain.append(('tax_inv_date', '>=', data['form']['date_from']))
            domain.append(('tax_inv_date', '<=', data['form']['date_to']))
            docs = self.env['account.invoice'].search(domain, order='tax_inv_date,tax_inv_no asc')

        # print "DOCS"
        # print docs

        return {
            'doc_ids': docids,
            'doc_model': 'account.invoice',
            'docs': docs,
            'company_id': company_id,
            'data': data['form'],
            'step': step,
        }



#start This is to generate purchase tax report
class report_purchase_tax_report(models.AbstractModel):
    _name = 'report.thai_accounting.purchase_tax_report_id'


    @api.model
    def _get_report_values(self, docids, data=None):
    # def get_report_values(self, docids, data=None):
        company_id = self.env.user.company_id

        domain =[('is_closing_month','=',False)]
        if data['form']['tax_id']:
            account_id = self.env['account.tax'].browse(data['form']['tax_id'][0]).account_id
            domain.append(('account_id', '=', account_id.id))
        if data['form']['date_from']:
            domain.append(('date', '>=', data['form']['date_from']))
        if data['form']['date_to']:
            domain.append(('date', '<=', data['form']['date_to']))
        # print domain
        docs = self.env['account.move.line'].search(domain, order='invoice_date asc')
        # print docs

        return {
            'doc_ids': docids,
            'doc_model': 'account.invoice',
            'docs': docs,
            'company_id': company_id,
            'data': data['form'],
        }
