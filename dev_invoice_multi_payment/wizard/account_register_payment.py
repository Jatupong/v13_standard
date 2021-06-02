# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle 
#
##############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import itertools
from operator import itemgetter
import operator
from datetime import date
from odoo.tools.float_utils import float_compare

MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
}

MAP_INVOICE_TYPE_PAYMENT_SIGN = {
    'out_invoice': 1,
    'in_refund': 1,
    'in_invoice': -1,
    'out_refund': -1,
}

class bulk_register_invoice(models.TransientModel):
    _name = 'bulk.register.invoice'
    
    invoice_id = fields.Many2one('account.move',string='Invoice')
    partner_id = fields.Many2one('res.partner',string='Partner')
    inv_amount = fields.Float('Original Amount')
    amount = fields.Float('Amount')
    paid_amount = fields.Float('Pay Amount') 
    bulk_invoice_id = fields.Many2one('account.register.payment')
    currency_id = fields.Many2one('res.currency', string='Currency')


class AccountRegisterPayment(models.Model):
    _inherit = 'account.register.payment'

    @api.model
    def default_get(self, fields):
        res = super(AccountRegisterPayment, self).default_get(fields)
        print ('---RES-AccountRegisterPayment-default_get')
        print (res)
        inv_ids = self._context.get('active_ids')
        vals = []
        invoice_ids = self.env['account.move'].browse(inv_ids)
        inv_type = ''
        for invo in invoice_ids:
            inv_type = invo.type
            break
        curr_pool = self.env['res.currency']
        comp_currency = self.env.user.company_id.currency_id
        for inv in invoice_ids:
            ############# REMOVE BY JA - 28/09/2020 ##########
            # if inv_type != inv.type:
            #     raise ValidationError('You must select only invoices or refunds.')
            ############# REMOVE BY JA - 28/09/2020 ##########
            if inv.state != 'posted':
                raise ValidationError('Please Select Open Invoices.')
            inv_currency = inv.currency_id
            pay_date = date.today()
            currency_id = comp_currency.with_context(date=pay_date)
            amount = curr_pool._compute(inv.currency_id, currency_id, inv.amount_residual) * MAP_INVOICE_TYPE_PAYMENT_SIGN[inv.type]
            inv_amt = curr_pool._compute(inv.currency_id, currency_id, inv.amount_total) * MAP_INVOICE_TYPE_PAYMENT_SIGN[inv.type]

            vals.append((0, 0, {
                'invoice_id': inv and inv.id or False,
                'partner_id': inv and inv.partner_id.id or False,
                'inv_amount': inv_amt or 0.0,
                'amount': amount or 0.0,
                'paid_amount': amount or 0.0,
                'currency_id': currency_id and currency_id.id or False,
            }))

        res.update({
            'invoice_register_ids': vals,
            'currency_id': self.env.user.company_id.currency_id and self.env.user.company_id.currency_id.id or False,
        })

        return res


    invoice_register_ids = fields.One2many('bulk.register.invoice', 'bulk_invoice_id', string='Invoice')
    # is_partial_selected_invoice = fields.Boolean(string='Partial Payment')

    def process_payment(self):
        # print ('---Partial Invoice Payment')
        vals=[]
        for line in self.invoice_register_ids:
            if abs(line.paid_amount) > 0.0:
                vals.append({
                    'invoice_id':line.invoice_id or False,
                    'partner_id':line.partner_id and line.partner_id.id or False,
                    'amount':line.amount or 0.0,
                    'paid_amount':abs(line.paid_amount) or 0.0,
                    'currency_id':line.invoice_id.currency_id.id or False,
                })
        new_vals=sorted(vals,key=itemgetter('partner_id'))
        if not self.group_payment:
            groups = itertools.groupby(new_vals, key=operator.itemgetter('invoice_id'))
            result = [{'invoice_id': k, 'values': [x for x in v]} for k, v in groups]
        else:
            groups = itertools.groupby(new_vals, key=operator.itemgetter('partner_id'))
            result = [{'partner_id':k,'values':[x for x in v]} for k, v in groups]

        new_payment_ids=[]
        # print ('RESULT--')
        # print (result)
        # print (x)
        is_multi = False
        if len(result) > 1:
            is_multi = True

        for res in result:
            line_list = []
            inv_ids = []
            payment_method_id= self.env['account.payment.method'].search([('name','=','Manual')],limit=1)
            if not payment_method_id:
                payment_method_id= self.env['account.payment.method'].search([],limit=1)
            payment_date = False
            if self.payment_date:
                payment_date = self.payment_date.strftime("%Y-%m-%d")


            write_off_amount = 0
            for writeoff_multi in self.writeoff_multi_acc_ids:
                write_off_amount += writeoff_multi.amount

            #####
            pay_val={
                'payment_type':self.payment_type,
                'payment_date':payment_date,
                # 'partner_type':self.partner_type,
                'payment_for':'multi_payment',
                'partner_id':res.get('partner_id'),
                'journal_id':self.journal_id and self.journal_id.id or False,
                #####################
                'communication':self.communication,
                'payment_account_id': self.payment_account_id.id,
                'post_diff_acc': self.post_diff_acc,
                'remark': self.remark,
                'cheque_bank': self.cheque_bank.id,
                'cheque_branch': self.cheque_branch,
                'cheque_number': self.cheque_number,
                'cheque_date': self.cheque_date,
                ######################
                'payment_method_id':payment_method_id and payment_method_id.id or False,
                'state':'draft',
                'currency_id':res.get('values')[0].get('currency_id'),
                'amount':self.amount,
                'writeoff_multi_acc_ids': [(4, writeoff_multi.id, None) for writeoff_multi in
                                           self.writeoff_multi_acc_ids],
                'line_ids': line_list,
                'invoice_ids': [(6, 0, inv_ids)],

            }

            paid_amt=0

            for inv_line in res.get('values'):
                invoice  = inv_line.get('invoice_id')
                inv_ids.append(invoice.id)
                full_reco=False
                if invoice.amount_residual == inv_line.get('paid_amount'):
                    full_reco = True
                line_list.append((0,0,{
                    'invoice_id':invoice.id,
                    'date':invoice.invoice_date,
                    'due_date':invoice.invoice_date_due,
                    'original_amount':invoice.amount_total,
                    'balance_amount':invoice.amount_residual,
                    'allocation':inv_line.get('paid_amount'),
                    'full_reconclle':full_reco,
                    # 'account_payment_id':payment_id and payment_id.id or False
                }))
                paid_amt += inv_line.get('paid_amount')

            if is_multi: #change amount for payment to paid amount without consider amount on payment screen, if not multi then follow amount on payment screen
                pay_val['amount'] = paid_amt

            payment_id = self.env['account.payment'].create(pay_val)

            # print ('---AMOUNT--')
            # print (paid_amt)
            # print (write_off_amount)

            # if is_multi:
            #     payment_id.write({
            #         'line_ids': line_list,
            #         'amount': paid_amt,
            #         'invoice_ids': [(6, 0, inv_ids)]
            #     })
            # else:
            #     payment_id.write({
            #         'line_ids':line_list,
            #         'invoice_ids':[(6,0,inv_ids)]
            #     })
            new_payment_ids.append(payment_id)


        payment_ids = []
        for pay in new_payment_ids:
            payment_ids.append(pay.id)
            pay.post()

        # print (new_payment_ids)
        action_vals = {
            'name': _('Payments'),
            'domain': [('id', 'in', payment_ids)],
            'res_model': 'account.payment',
            'view_id': False,
            'type': 'ir.actions.act_window',
        }

        if len(new_payment_ids) == 1:
            action_vals.update({'res_id': new_payment_ids[0].id, 'view_mode': 'form'})
        else:
            action_vals['view_mode'] = 'tree,form'
        return action_vals

    @api.onchange('invoice_register_ids','invoice_register_ids.paid_amount')
    def onchange_invoice_register_ids(self):
        due_amount = 0
        paid_amount = 0
        if self.invoice_register_ids:
            for line in self.invoice_register_ids:
                due_amount += line.amount
                paid_amount += line.paid_amount

            if float_compare(float(abs(due_amount)), float(abs(paid_amount)),precision_digits=2) != 0:
                # self.is_partial_selected_invoice = True
                self.payment_difference_handling = 'open'


    def check_partial_payment(self):
        due_amount = 0
        paid_amount = 0
        if self.invoice_register_ids:
            for line in self.invoice_register_ids:
                due_amount += line.amount
                paid_amount += line.paid_amount

            if float_compare(float(abs(due_amount)), float(abs(paid_amount)), precision_digits=2) != 0:
                return True
            else:
                return False
        else:
            return False

    # @api.onchange('currency_id')
    # def onchange_currency_id(self):
    #     curr_pool = self.env['res.currency']
    #     if self.currency_id:
    #         # print ('------CURRENCY')
    #         # print (self.currency_id)
    #         for invoice in self.invoice_register_ids:
    #             if self.currency_id.id != invoice.currency_id.id:
    #                 currency_id = self.currency_id.with_context(date=self.payment_date)
    #                 amount = curr_pool._compute(invoice.currency_id, currency_id, invoice.amount)
    #                 paid_amount = curr_pool._compute(invoice.currency_id, currency_id, invoice.paid_amount)
    #                 inv_amount = curr_pool._compute(invoice.currency_id, currency_id, invoice.inv_amount)
    #                 invoice.inv_amount = inv_amount
    #                 invoice.amount = amount
    #                 invoice.paid_amount = paid_amount
    #                 invoice.currency_id = self.currency_id.id


    ################Replace create_payments in account_register_payment file in Thai_Accounting#######Jatupong - 28/04/2020
    # @api.multi
    def create_payments(self):
        print('------create_payments#2')
        vals = []
        # print ('-----------')
        print('INVOICE-MULTI-create_payments-2')
        if not self.check_partial_payment():
            print('---SIMPLE PAYMENT--')
            return super(AccountRegisterPayment, self).create_payments()
        else:
            return self.process_payment()

    @api.onchange('writeoff_multi_acc_ids','invoice_register_ids')
    def onchange_writeoff_multi_accounts(self):
        for payment in self:
            if payment.check_partial_payment() and payment.invoice_register_ids:
                due_amount = paid_amount = diff_amount = 0
                for line in payment.invoice_register_ids:
                    due_amount += line.amount
                    paid_amount += line.paid_amount

                if payment.writeoff_multi_acc_ids:
                    diff_amount = sum([line.amount for line in payment.writeoff_multi_acc_ids])

                payment.amount = abs(paid_amount) - diff_amount
                payment.amount_untaxed = sum([invoice.amount_untaxed for invoice in payment.invoice_ids])
            else:
                super(AccountRegisterPayment, payment).onchange_writeoff_multi_accounts()
