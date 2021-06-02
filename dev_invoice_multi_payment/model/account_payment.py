# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle 
#
##############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError

# Since invoice amounts are unsigned, this is how we know if money comes in or goes out
MAP_INVOICE_TYPE_PAYMENT_SIGN = {
    'out_invoice': -1,
    'in_refund': -1,
    'in_invoice': 1,
    'out_refund': 1,
}

class account_move(models.Model):
    _inherit='account.move'
    
    inv_id = fields.Many2one('account.move', string='Invoice')

class account_move_line(models.Model):
    _inherit = 'account.move.line'

    inv_id = fields.Many2one('account.move', string='Invoice')

class account_payment(models.Model):
    _inherit = 'account.payment'

    payment_for = fields.Selection([('multi_payment', 'Multiple Payment')], string='Payment Method')
    line_ids = fields.One2many('advance.payment.line', 'account_payment_id')
    full_reco = fields.Boolean('Full Reconcile')
    allocation_amount = fields.Float('Total Amount', compute='get_allocation_amount')
    
    @api.depends('line_ids','line_ids.allocation')
    def get_allocation_amount(self):
        for payment in self:
            amount = 0
            payment.allocation_amount = 0
            for line in payment.line_ids:
                amount += line.allocation
            payment.allocation_amount = amount
            
    
    @api.onchange('payment_for')
    def onchange_payment_for(self):
        for payment in self:
            if payment.payment_for != 'multi_payment':
                for line in payment.line_ids:
                    line.unlink()

    @api.onchange('currency_id')
    def onchange_currency(self):
        curr_pool = self.env['res.currency']
        for payment in self:
            if payment.currency_id and payment.line_ids:
                for line in payment.line_ids:
                    if line.currency_id.id != payment.currency_id.id:
                        currency_id = payment.currency_id.with_context(date=payment.payment_date)
                        line.original_amount = curr_pool._compute(line.currency_id, currency_id, line.original_amount,
                                                                  round=True)
                        line.balance_amount = curr_pool._compute(line.currency_id, currency_id, line.balance_amount,
                                                                 round=True)
                        line.allocation = curr_pool._compute(line.currency_id, currency_id, line.allocation, round=True)
                        line.currency_id = payment.currency_id and payment.currency_id.id or False

        
    
    def remove_lines(self):
        invoice_ids = []
        if self.line_ids and self.payment_for == 'multi_payment':
            for line in self.line_ids:
                if line.allocation:
                    invoice_ids.append(line.invoice_id.id)
                else:
                    line.unlink()
        self.invoice_ids = [(6,0, invoice_ids)]
        
    
    
    # def create_other_lines(self,amount):
    #     company_currency = self.company_id.currency_id
    #     if self.payment_type in ('outbound', 'transfer'):
    #         counterpart_amount = amount
    #         liquidity_line_account = self.journal_id.default_debit_account_id
    #     else:
    #         counterpart_amount = -amount
    #         liquidity_line_account = self.journal_id.default_credit_account_id
    #
    #     # Manage currency.
    #     if self.currency_id == company_currency:
    #         # Single-currency.
    #         balance = counterpart_amount
    #         counterpart_amount = 0.0
    #         currency_id = False
    #     else:
    #         # Multi-currencies.
    #         balance = self.currency_id._convert(counterpart_amount, company_currency, self.company_id, self.payment_date)
    #         currency_id = self.currency_id.id
    #
    #     # Manage custom currency on journal for liquidity line.
    #     if self.journal_id.currency_id and self.currency_id != self.journal_id.currency_id:
    #         # Custom currency on journal.
    #         liquidity_line_currency_id = self.journal_id.currency_id.id
    #         liquidity_amount = company_currency._convert(
    #             balance, self.journal_id.currency_id, self.company_id, self.payment_date)
    #     else:
    #         # Use the payment currency.
    #         liquidity_line_currency_id = currency_id
    #         liquidity_amount = counterpart_amount
    #
    #     # Compute 'name' to be used in receivable/payable line.
    #     rec_pay_line_name = ''
    #     if self.payment_type == 'transfer':
    #         rec_pay_line_name = self.name
    #     else:
    #         if self.partner_type == 'customer':
    #             if self.payment_type == 'inbound':
    #                 rec_pay_line_name += _("Customer Payment")
    #             elif self.payment_type == 'outbound':
    #                 rec_pay_line_name += _("Customer Credit Note")
    #         elif self.partner_type == 'supplier':
    #             if self.payment_type == 'inbound':
    #                 rec_pay_line_name += _("Vendor Credit Note")
    #             elif self.payment_type == 'outbound':
    #                 rec_pay_line_name += _("Vendor Payment")
    #
    #     if self.payment_type == 'transfer':
    #         liquidity_line_name = _('Transfer to %s') % self.destination_journal_id.name
    #     else:
    #         liquidity_line_name = self.name
    #     move_vals = {
    #         'date': self.payment_date,
    #         'ref': self.communication,
    #         'journal_id': self.journal_id.id,
    #         'currency_id': self.journal_id.currency_id.id or self.company_id.currency_id.id,
    #         'partner_id': self.partner_id.id,
    #         'line_ids': [
    #             # Receivable / Payable / Transfer line.
    #             (0, 0, {
    #                 'name': rec_pay_line_name,
    #                 'amount_currency': counterpart_amount,
    #                 'currency_id': currency_id,
    #                 'debit': balance > 0.0 and balance or 0.0,
    #                 'credit': balance < 0.0 and -balance or 0.0,
    #                 'date_maturity': self.payment_date,
    #                 'partner_id': self.partner_id.id,
    #                 'account_id': self.destination_account_id.id,
    #                 'payment_id': self.id,
    #             }),
    #             # Liquidity line.
    #             (0, 0, {
    #                 'name': liquidity_line_name,
    #                 'amount_currency': -liquidity_amount,
    #                 'currency_id': liquidity_line_currency_id,
    #                 'debit': balance < 0.0 and -balance or 0.0,
    #                 'credit': balance > 0.0 and balance or 0.0,
    #                 'date_maturity': self.payment_date,
    #                 'partner_id': self.partner_id.id,
    #                 'account_id': liquidity_line_account.id,
    #                 'payment_id': self.id,
    #             }),
    #         ],
    #     }
    #     moves = self.env['account.move'].create(move_vals)
    #     moves.post()
    #     return True

    #remove and apply from thai accounting instead
    # def _dev_prepare_write_off_move_line(self):
    #     # print ('--_dev_prepare_write_off_move_line')
    #     for payment in self:
    #         write_off_move_line = False
    #         # print (payment.writeoff_multi_acc_ids)
    #
    #         if payment.writeoff_multi_acc_ids:
    #             payment.write({'post_diff_acc': 'multi'})
    #             # print('---GOT---writeoff_multi_acc_ids--')
    #             company_currency = payment.company_id.currency_id
    #             for write_off_line in payment.writeoff_multi_acc_ids:
    #                 # print('WRITE OFF LINE--')
    #                 # print(write_off_line.name)
    #                 # print(write_off_line.amount)
    #                 # print(write_off_line.wht_type)
    #                 # print(write_off_line.writeoff_account_id.id)
    #                 if payment.currency_id == company_currency:
    #                     write_off_balance = 0.0
    #                     currency_id = False
    #                 else:
    #                     write_off_balance = payment.currency_id._convert(write_off_line.amount, company_currency,
    #                                                                      payment.company_id, payment.payment_date)
    #                     currency_id = payment.currency_id.id
    #
    #                 if payment.partner_type == 'customer':
    #                     # print('---CUSTOMER--write-off')
    #                     write_off_move_line = (0, 0, {
    #                         'name': write_off_line.name,
    #                         'amount_currency': write_off_balance,
    #                         'currency_id': currency_id,
    #                         'debit': -write_off_line.amount < 0.0 and write_off_line.amount or 0.0,
    #                         'credit': -write_off_line.amount > 0.0 and -write_off_line.amount or 0.0,
    #                         'date_maturity': payment.payment_date,
    #                         'partner_id': payment.partner_id.commercial_partner_id.id,
    #                         'account_id': write_off_line.writeoff_account_id.id,
    #                         'payment_id': payment.id,
    #                         'wht_tax': write_off_line.deduct_item_id.id or False,
    #                         'wht_type': write_off_line.wht_type.id or False,
    #                         'amount_before_tax': write_off_line.amount_untaxed or 0.00,
    #                     })
    #                 else:
    #                     write_off_move_line = (0, 0, {
    #                         'name': write_off_line.name,
    #                         'amount_currency': write_off_balance,
    #                         'currency_id': currency_id,
    #                         'debit': -write_off_line.amount > 0.0 and -write_off_line.amount or 0.0,
    #                         'credit': -write_off_line.amount < 0.0 and write_off_line.amount or 0.0,
    #                         'date_maturity': payment.payment_date,
    #                         'partner_id': payment.partner_id.commercial_partner_id.id,
    #                         'account_id': write_off_line.writeoff_account_id.id,
    #                         'payment_id': payment.id,
    #                         'wht_tax': write_off_line.deduct_item_id.id or False,
    #                         'wht_type': write_off_line.wht_type.id or False,
    #                         'amount_before_tax': write_off_line.amount_untaxed or 0.00,
    #                     })
    #         # print (write_off_move_line)
    #         # print (x)
    #         return write_off_move_line

    #replace by inherit from prepare_payment_moves
    # def _dev_prepare_payment_moves(self):
    #     all_move_vals = []
    #     line_val = []
    #     move_names = ""
    #     liquidity_line_name = ""
    #
    #     liquidity_amount_total = balance_total = 0
    #     for payment in self:
    #         liquidity_line_currency_id = payment.currency_id.id
    #
    #         if payment.payment_type in ('outbound', 'transfer'):
    #             liquidity_line_account = payment.journal_id.default_debit_account_id
    #         else:
    #             liquidity_line_account = payment.journal_id.default_credit_account_id
    #
    #         move_vals = {
    #             'date': payment.payment_date,
    #             'ref': payment.communication,
    #             'journal_id': payment.journal_id.id,
    #             'currency_id': payment.journal_id.currency_id.id or payment.company_id.currency_id.id,
    #             'partner_id': payment.partner_id.id,
    #             'line_ids': line_val,
    #         }
    #
    #         for line in self.line_ids:
    #             if abs(line.allocation) <= 0:
    #                 continue
    #             o_move = []
    #             company_currency = payment.company_id.currency_id
    #             move_names = payment.move_name.split(
    #                 payment._get_move_name_transfer_separator()) if payment.move_name else None
    #
    #             # Compute amounts.
    #             if payment.payment_type in ('outbound', 'transfer'):
    #                 counterpart_amount = line.allocation
    #                 liquidity_line_account = payment.journal_id.default_debit_account_id
    #             else:
    #                 counterpart_amount = -line.allocation
    #                 liquidity_line_account = payment.journal_id.default_credit_account_id
    #
    #             # Manage currency.
    #             if payment.currency_id == company_currency:
    #                 # Single-currency.
    #                 balance = counterpart_amount
    #                 counterpart_amount = 0.0
    #                 currency_id = False
    #                 balance_total += balance
    #             else:
    #                 # Multi-currencies.
    #                 balance = payment.currency_id._convert(counterpart_amount, company_currency, payment.company_id,
    #                                                        payment.payment_date)
    #                 currency_id = payment.currency_id.id
    #                 balance_total += balance
    #
    #             # Manage custom currency on journal for liquidity line.
    #             if payment.journal_id.currency_id and payment.currency_id != payment.journal_id.currency_id:
    #                 # Custom currency on journal.
    #                 liquidity_line_currency_id = payment.journal_id.currency_id.id
    #                 liquidity_amount = company_currency._convert(
    #                     balance, payment.journal_id.currency_id, payment.company_id, payment.payment_date)
    #                 liquidity_amount_total += liquidity_amount
    #             else:
    #                 # Use the payment currency.
    #                 liquidity_line_currency_id = currency_id
    #                 liquidity_amount = counterpart_amount
    #                 liquidity_amount_total += liquidity_amount
    #
    #             # Compute 'name' to be used in receivable/payable line.
    #             rec_pay_line_name = ''
    #             if payment.payment_type == 'transfer':
    #                 rec_pay_line_name = payment.name
    #             else:
    #                 if payment.partner_type == 'customer':
    #                     if payment.payment_type == 'inbound':
    #                         rec_pay_line_name += _("Customer Payment")
    #                     elif payment.payment_type == 'outbound':
    #                         rec_pay_line_name += _("Customer Credit Note")
    #                 elif payment.partner_type == 'supplier':
    #                     if payment.payment_type == 'inbound':
    #                         rec_pay_line_name += _("Vendor Credit Note")
    #                     elif payment.payment_type == 'outbound':
    #                         rec_pay_line_name += _("Vendor Payment")
    #                 if payment.invoice_ids:
    #                     rec_pay_line_name += ': %s' % ', '.join(line.invoice_id.mapped('name'))
    #
    #             # Compute 'name' to be used in liquidity line.
    #             if payment.payment_type == 'transfer':
    #                 liquidity_line_name = _('Transfer to %s') % payment.destination_journal_id.name
    #             else:
    #                 liquidity_line_name = payment.name
    #
    #             # ==== 'inbound' / 'outbound' ====
    #
    #             # Receivable / Payable / Transfer line.
    #             line_val.append((0, 0, {
    #                 'name': rec_pay_line_name,
    #                 'amount_currency': counterpart_amount,
    #                 'currency_id': currency_id,
    #                 'debit': balance > 0.0 and balance or 0.0,
    #                 'credit': balance < 0.0 and -balance or 0.0,
    #                 'date_maturity': payment.payment_date,
    #                 'partner_id': payment.partner_id.id,
    #                 'account_id': payment.destination_account_id.id,
    #                 'payment_id': payment.id,
    #                 'inv_id': line.invoice_id.id,
    #             }))
    #
    #         # add write off line
    #         write_off_line = payment._dev_prepare_write_off_move_line()
    #         write_off_amount = 0
    #         if write_off_line:
    #             line_val.append(write_off_line)
    #             # print (write_off_line[0])
    #             # print (write_off_line[1])
    #             # print(write_off_line[2]['debit'])
    #             if write_off_line[2]['debit']:
    #                 write_off_amount = write_off_line[2]['debit']
    #                 balance_total = balance_total + write_off_amount
    #             else:
    #                 write_off_amount = write_off_line[2]['credit']
    #                 balance_total = balance_total - write_off_amount
    #
    #
    #         #combine liqudity line
    #         # Liquidity line.
    #         # print ('PAYMENT AMOUNT')
    #         # print (payment.amount)
    #         # print (MAP_INVOICE_TYPE_PAYMENT_SIGN[payment.invoice_ids[0].type])
    #         # print (payment.invoice_ids[0].type)
    #         # print (balance_total)
    #         # balance_total = payment.amount * MAP_INVOICE_TYPE_PAYMENT_SIGN[payment.invoice_ids[0].type]
    #         # print (x)
    #
    #         # balance_total = balance_total - abs(write_off_amount)
    #
    #         line_val.append((0, 0, {
    #             'name': liquidity_line_name,
    #             'amount_currency': -liquidity_amount_total,
    #             'currency_id': liquidity_line_currency_id,
    #             'debit': balance_total < 0.0 and -balance_total or 0.0,
    #             'credit': balance_total > 0.0 and balance_total or 0.0,
    #             'date_maturity': payment.payment_date,
    #             'partner_id': payment.partner_id.id,
    #             'account_id': liquidity_line_account.id,
    #             'payment_id': payment.id
    #         }))
    #
    #         #### add write off line
    #
    #
    #         if move_names:
    #             move_vals['name'] = move_names[0]
    #
    #         print('MOVE VALS')
    #         print(move_vals)
    #         # print (y)
    #         AccountMove = self.env['account.move'].with_context(default_type='entry')
    #         moves = AccountMove.create(move_vals)
    #         moves.filtered(lambda move: move.journal_id.post_at != 'bank_rec').post()
    #         move_name = self._get_move_name_transfer_separator().join(moves.mapped('name'))
    #
    #         for line in self.line_ids:
    #             # reconcile per line with condition of invoice id
    #             if payment.payment_type in ('inbound', 'outbound'):
    #                 if line.invoice_id:
    #                     (moves + line.invoice_id).line_ids \
    #                         .filtered(
    #                         lambda l: not l.reconciled and l.account_id == payment.destination_account_id and (
    #                                     l.move_id == line.invoice_id or l.inv_id == line.invoice_id)) \
    #                         .reconcile()
    #
    #         pay_amt = "{:.2f}".format(self.amount)
    #         amt = "{:.2f}".format(self.allocation_amount)
    #         pay_amt = float(pay_amt)
    #         amt = float(amt)
    #         # if pay_amt > amt:
    #         #     other_amount = pay_amt - amt
    #         #     payment.create_other_lines(other_amount)
    #
    #         payment.write({'amount': abs(balance_total)})
    #         # payment.write({'state': 'posted', 'move_name': move_name})
    #     return True

    def _prepare_payment_moves(self):
        for payment in self:
            if payment.line_ids and payment.payment_for == 'multi_payment':
                all_move_vals = []
                line_val = []
                move_names = ""
                liquidity_line_name = ""

                liquidity_amount_total = balance_total = 0
                for payment in self:
                    liquidity_line_currency_id = payment.currency_id.id

                    if payment.payment_type in ('outbound', 'transfer'):
                        liquidity_line_account = payment.journal_id.default_debit_account_id
                    else:
                        liquidity_line_account = payment.journal_id.default_credit_account_id

                    move_vals = {
                        'date': payment.payment_date,
                        'ref': payment.communication,
                        'journal_id': payment.journal_id.id,
                        'currency_id': payment.journal_id.currency_id.id or payment.company_id.currency_id.id,
                        'partner_id': payment.partner_id.id,
                        'line_ids': line_val,
                    }

                    for line in self.line_ids:
                        if abs(line.allocation) <= 0:
                            continue
                        o_move = []
                        company_currency = payment.company_id.currency_id
                        move_names = payment.move_name.split(
                            payment._get_move_name_transfer_separator()) if payment.move_name else None

                        # Compute amounts.
                        if payment.payment_type in ('outbound', 'transfer'):
                            counterpart_amount = line.allocation
                            liquidity_line_account = payment.journal_id.default_debit_account_id
                        else:
                            counterpart_amount = -line.allocation
                            liquidity_line_account = payment.journal_id.default_credit_account_id

                        # Manage currency.
                        if payment.currency_id == company_currency:
                            # Single-currency.
                            balance = counterpart_amount
                            counterpart_amount = 0.0
                            currency_id = False
                            balance_total += balance
                        else:
                            # Multi-currencies.
                            balance = payment.currency_id._convert(counterpart_amount, company_currency, payment.company_id,
                                                                   payment.payment_date)
                            currency_id = payment.currency_id.id
                            balance_total += balance

                        # Manage custom currency on journal for liquidity line.
                        if payment.journal_id.currency_id and payment.currency_id != payment.journal_id.currency_id:
                            # Custom currency on journal.
                            liquidity_line_currency_id = payment.journal_id.currency_id.id
                            liquidity_amount = company_currency._convert(
                                balance, payment.journal_id.currency_id, payment.company_id, payment.payment_date)
                            liquidity_amount_total += liquidity_amount
                        else:
                            # Use the payment currency.
                            liquidity_line_currency_id = currency_id
                            liquidity_amount = counterpart_amount
                            liquidity_amount_total += liquidity_amount

                        # Compute 'name' to be used in receivable/payable line.
                        rec_pay_line_name = ''
                        if payment.payment_type == 'transfer':
                            rec_pay_line_name = payment.name
                        else:
                            if payment.partner_type == 'customer':
                                if payment.payment_type == 'inbound':
                                    rec_pay_line_name += _("Customer Payment")
                                elif payment.payment_type == 'outbound':
                                    rec_pay_line_name += _("Customer Credit Note")
                            elif payment.partner_type == 'supplier':
                                if payment.payment_type == 'inbound':
                                    rec_pay_line_name += _("Vendor Credit Note")
                                elif payment.payment_type == 'outbound':
                                    rec_pay_line_name += _("Vendor Payment")
                            if payment.invoice_ids:
                                rec_pay_line_name += ': %s' % ', '.join(line.invoice_id.mapped('name'))

                        # Compute 'name' to be used in liquidity line.
                        if payment.payment_type == 'transfer':
                            liquidity_line_name = _('Transfer to %s') % payment.destination_journal_id.name
                        else:
                            liquidity_line_name = payment.name

                        # ==== 'inbound' / 'outbound' ====

                        # Receivable / Payable / Transfer line.
                        line_val.append((0, 0, {
                            'name': rec_pay_line_name,
                            'amount_currency': counterpart_amount,
                            'currency_id': currency_id,
                            'debit': balance > 0.0 and balance or 0.0,
                            'credit': balance < 0.0 and -balance or 0.0,
                            'date_maturity': payment.payment_date,
                            'partner_id': payment.partner_id.id,
                            'account_id': payment.destination_account_id.id,
                            'payment_id': payment.id,
                            'inv_id': line.invoice_id.id,
                        }))


                    line_val.append((0, 0, {
                        'name': liquidity_line_name,
                        'amount_currency': -liquidity_amount_total,
                        'currency_id': liquidity_line_currency_id,
                        'debit': balance_total < 0.0 and -balance_total or 0.0,
                        'credit': balance_total > 0.0 and balance_total or 0.0,
                        'date_maturity': payment.payment_date,
                        'partner_id': payment.partner_id.id,
                        'account_id': liquidity_line_account.id,
                        'payment_id': payment.id
                    }))

                    #### add write off line


                    if move_names:
                        move_vals['name'] = move_names[0]

                    # print('MOVE VALS')
                    # print(move_vals)
                    # print (y)
                    all_move_vals.append(move_vals)

                # print ('BEFORE')
                # print (all_move_vals)
                all_move_vals = payment._prepare_write_off_line(all_move_vals)
                # print('After')
                # print (all_move_vals)
                # print (x)
                return all_move_vals
            else:
                #no partial payment then follow the standard
                return super(account_payment, self)._prepare_payment_moves()
    
    def check_multi_payment(self):
        pay_amt = "{:.2f}".format(self.amount)
        amt = "{:.2f}".format(self.allocation_amount)
        pay_amt = float(pay_amt)
        amt = float(amt)
        if not amt and not self.amount:
            raise ValidationError(("Add Allocation Amount in payment item"))

        # if pay_amt < amt:
        #     raise ValidationError(("Amount is must be greater or equal '%s'") %(amt))
        return True
    
    def post(self):
        # print ('last post')
        # print (self.name)
        # print (self.move_name)


        for payment in self:
            if payment.payment_for == 'multi_payment':
                # print('PAYMENT MULTI')
                payment.check_multi_payment()
                # print(payment.invoice_ids)
                #keep temp invoice to reconcile here, otherwise odoo standard will be reconcile instead
                temp_invoice_ids = payment.invoice_ids
                payment.update({
                    'invoice_ids': [(5, 0, 0)],
                })
                # print (payment.invoice_ids)
                # print ('BEFORE SUPER')
                # print (x)
                #do all except reconcile and let system do manually below

                super(account_payment, payment).post()

                for line in self.line_ids:
                    # reconcile per line with condition of invoice id
                    #this process make invoice_ids from reconcile process
                    if payment.payment_type in ('inbound', 'outbound'):
                        if line.invoice_id:
                            (payment.move_line_ids[0].move_id + line.invoice_id).line_ids \
                                .filtered(
                                lambda l: not l.reconciled and l.account_id == payment.destination_account_id and (
                                            l.move_id == line.invoice_id or l.inv_id == line.invoice_id)) \
                                .reconcile()

                #update invoice_ids back
                # payment.update({
                #     'invoice_ids': [(6, 0, temp_invoice_ids.ids)],
                # })
                # update payment refund for future use it, this is one of the function from Thai accounting
                payment.create_payment_refund_record()
                # print (payment.invoice_ids)
                # print ('Post by DEV INVOICE MULTI')

                return True
            else:
                return super(account_payment,payment).post()

    @api.onchange('writeoff_multi_acc_ids', 'line_ids')
    def onchange_writeoff_multi_accounts(self):
        for payment in self:
            if payment.payment_for== 'multi_payment':
                due_amount = paid_amount = diff_amount = 0
                for line in payment.line_ids:
                    due_amount += line.balance_amount
                    paid_amount += line.allocation

                if payment.writeoff_multi_acc_ids:
                    diff_amount = sum([line.amount for line in payment.writeoff_multi_acc_ids])
                # print ('MULTI--')
                # print (paid_amount)
                # print (diff_amount)
                payment.amount = paid_amount - diff_amount
                payment.amount_untaxed = sum([invoice.amount_untaxed for invoice in payment.invoice_ids])
            else:
                super(account_payment, payment).onchange_writeoff_multi_accounts()

    def load_payment_lines(self):
        if self.payment_for == 'multi_payment':
            self.line_ids.unlink()
            account_inv_obj = self.env['account.move']
            invoice_ids=[]
            partner_ids = self.env['res.partner'].search([('parent_id','=',self.partner_id.id)]).ids
            partner_ids.append(self.partner_id.id)
            query = """ select id from account_move where partner_id in %s and state = %s and type in %s and company_id = %s and invoice_payment_state = %s"""
            if self.partner_type == 'customer':
                params = (tuple(partner_ids),'posted',('out_invoice','out_refund'), self.company_id.id, 'not_paid')
            else:
                params = (tuple(partner_ids),'posted',('in_invoice','in_refund'), self.company_id.id, 'not_paid')
            self.env.cr.execute(query, params)
            result = self.env.cr.dictfetchall()
            invoice_ids = [inv.get('id') for inv in result]
            invoice_ids = account_inv_obj.browse(invoice_ids)
            curr_pool = self.env['res.currency']
            for vals in invoice_ids:
                account_id = False
                if self.partner_type == 'customer':
                    account_id = vals.partner_id and vals.partner_id.property_account_receivable_id.id or False
                else:
                    account_id = vals.partner_id and vals.partner_id.property_account_payable_id.id or False
                    
                original_amount = vals.amount_total
                balance_amount = vals.amount_residual
                allocation = vals.amount_residual
                if vals.currency_id.id != self.currency_id.id:
                    original_amount = vals.amount_total
                    balance_amount = vals.amount_residual
                    allocation = vals.amount_residual
                    if vals.currency_id.id != self.currency_id.id:
                        currency_id = self.currency_id.with_context(date=self.payment_date)
                        original_amount = curr_pool._compute(vals.currency_id, currency_id, original_amount, round=True)
                        balance_amount = curr_pool._compute(vals.currency_id, currency_id, balance_amount, round=True)
                        allocation = curr_pool._compute(vals.currency_id, currency_id, allocation, round=True)

                query = """ INSERT INTO advance_payment_line (invoice_id, account_id, date, due_date, original_amount, balance_amount, currency_id, account_payment_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"""
                params = (vals.id,account_id, vals.invoice_date, vals.invoice_date_due, original_amount, balance_amount, self.currency_id.id, self.id)
                self.env.cr.execute(query, params)
            self.invoice_ids = [(6,0, invoice_ids.ids)] 
            
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
