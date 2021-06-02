# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval as eval
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_is_zero, float_compare

# mapping invoice type to journal type
TYPE2JOURNAL = {
    'out_invoice': 'sale',
    'in_invoice': 'purchase',
    'out_refund': 'sale',
    'in_refund': 'purchase',
}

# mapping invoice type to refund type
TYPE2REFUND = {
    'out_invoice': 'out_refund',        # Customer Invoice
    'in_invoice': 'in_refund',          # Vendor Bill
    'out_refund': 'out_invoice',        # Customer Refund
    'in_refund': 'in_invoice',          # Vendor Refund
}

MAGIC_COLUMNS = ('id', 'create_uid', 'create_date', 'write_uid', 'write_date')

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    payment_id = fields.Many2one('account.payment',string='Payment',copy=False)


class account_payment(models.Model):
    _inherit = "account.payment"

    @api.multi
    def post(self):
        for payment in self:
            if payment.company_id.country_id.name == 'Thailand':
                precision = self.env['decimal.precision'].precision_get('Product Price')
                if payment.payment_difference_handling == 'reconcile' and payment.post_diff_acc == 'multi':
                    amount = 0
                    ########### this is diff to put in simple "write off account"
                    amount_final_diff = 0

                    # caculate total write off amount
                    if payment.writeoff_multi_acc_ids:
                        for write_off_line in payment.writeoff_multi_acc_ids:
                            amount += write_off_line.amount
                    if payment.writeoff_account_id and float_compare(float(payment.payment_difference), float(amount),
                                                                        precision_digits=precision) != 0:
                            amount_final_diff = payment.payment_difference - amount


                    # recheck to ensure that writeoff amount is the same with payment difference
                    #print "********************"
                    #print self.payment_difference
                    #print amount
                    #print amount_final_diff
                    #print "********************"
                    if payment.payment_type == 'inbound' and float_compare(float(payment.payment_difference), float(amount+amount_final_diff),
                                                                        precision_digits=precision) != 0:
                        raise UserError(
                            _("The sum of write off amounts customer and payment difference amounts are not equal."))
                    elif payment.payment_type == 'outbound' and float_compare(float(payment.payment_difference), float((-1)*(amount+amount_final_diff)),
                                                                           precision_digits=precision) != 0:
                        raise UserError(
                            _("The sum of write off amounts supplier and payment difference amounts are not equal."))

                # if customer invoice and not generate tax invoice, then will automatically generate and also will do tax reverse if require.
                if payment.invoice_ids and payment.invoice_ids[0].type in ('out_invoice'):
                    for invoice in payment.invoice_ids:
                        if not invoice.tax_inv_generated and self.env.user.company_id.invoice_step == '2step':
                            invoice.action_generate_tax_inv()

                # if vendor bill require reverse tax
                # if self.invoice_ids and self.invoice_ids[0].type in ('in_invoice'):
                #     for invoice in self.invoice_ids:
                #         invoice.action_move_tax_reverse_create()

                # if payment by cheque
                if payment.bank_cheque:
                    # print "yes cheque"
                    if payment.invoice_ids and payment.invoice_ids[0].type in ('out_invoice', 'in_refund'):
                        type = 'rec'
                    else:
                        type = 'pay'
                    vals_cheque_rec = {
                        'issue_date': payment.payment_date,
                        'ref': payment.communication,
                        'cheque_bank': payment.cheque_bank.id,
                        'partner_id': payment.partner_id.id,
                        'cheque_branch': payment.cheque_branch,
                        'cheque_number': payment.cheque_number,
                        'cheque_date': payment.cheque_date,
                        'amount': payment.amount,
                        'journal_id': payment.journal_id.id,
                        'user_id': self.env.user.id,
                        'communication': payment.remark,
                        'company_id': payment.env.user.company_id.id,
                        'type': type,
                        'payment_id': payment.id,
                    }
                    self.cheque_reg_id = self.env['account.cheque.statement'].create(vals_cheque_rec).id

                # add payment to each invoice
                if payment.invoice_ids:
                    for inv in payment.invoice_ids:
                        inv.write({'payment_id': payment.id})

        return super(account_payment, self).post()
