# -*- coding: utf-8 -*-
# Copyright (C) 2016-2017  Technaureus Info Solutions(<http://technaureus.com/>).

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import calendar
import pytz

def strToDate(dt):
    return date(int(dt[0:4]), int(dt[5:7]), int(dt[8:10]))

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def _get_default_invoice_step(self):
        #if company setting is done then get from compnay, otherwise set default to 2 step
        if self.env.user.company_id.invoice_step:
            return self.env.user.company_id.invoice_step
        else:
            # print self.env.user.company_id.payment_with_deduct
            return '2step'

    date_invoice = fields.Date(string='Invoice Date',index=True,readonly=False,help="Keep empty to use the current date", copy=False)
    reference = fields.Char(string='Vendor Reference',
                            help="The partner reference of this invoice.", readonly=True,
                            states={'draft': [('readonly', False)],'open': [('readonly', False)]})


    bill_date = fields.Date(string='Schedule Bill Date',copy=False)
    bill_date_str = fields.Char(string='Schedule Bill Date', compute='_get_string_date', store=True, copy=False)
    invoice_step = fields.Selection([('1step', 'Invoice/Tax Invoice'), ('2step', 'Invoice--->Tax Invoice')],
                                    default=lambda self: self.env.user.company_id.invoice_step,
                                    help='1step is invoice and tax invoice is the same, 2 step is invoice and tax invoice is difference number')



    #############for credit note only ###########
    # is_manual_cn = fields.Boolean(string='Manual CN',default=False)
    # ref_tax_invoice_number = fields.Char(string='Ref Inv')
    # ref_tax_invoice_date = fields.Date(string='Ref Inv Date')
    # ref_tax_invoice_amount = fields.Float(string='Ref Inv Amt')
    #############for credit note only ###########

    ############### for company which can issue with tax or none-tax
    tax_id = fields.Many2one('account.tax',string='Tax ID',compute='_get_tax_id',store=True)

    ###################additional field ###################
    account_note = fields.Text(string='Note for Account', readonly=True, states={'draft': [('readonly', False)]},
                               copy=False)
    tax_inv_no = fields.Char(string='Tax Invoice No.', readonly=True, copy=False)
    tax_inv_date = fields.Date(string='Tax Invoice Date', help='Tax Invoice Number generated date.', copy=False)
    tax_inv_generated = fields.Boolean(string='Tax Invoice Generated', default=False, copy=False)

    adjust_move_id = fields.Many2one('account.move', string="Tax Journal Entry", copy=False)
    adjust_require = fields.Boolean(string="Tax Adjust Require", default=False)
    contact_person = fields.Many2one('res.partner', string="Contact Person")
    is_skip_gl = fields.Boolean(string='New Invoice Without GL', copy=False)


    ################### additional remove ###########
    # readonly_date_invoice = fields.Boolean(string='Readonly Date Invoice',
    #                                        default=lambda self: self.env.user.company_id.readonly_date_invoice)
    # allow_invoice_backward = fields.Boolean(string='Allow Record Invoice Backward',
    #                                         default=lambda self: self.env.user.company_id.allow_invoice_backward)

    # is_skip_gl_original = fields.Boolean(string='Invoice Without GL Original', copy=False)
    # original_date_inv_skip_gl = fields.Date(string='Original Date Invoice',copy=False)
    # print_tax_invoice = fields.Boolean(string='พิมพ์ใบกำกับภาษีแล้ว',copy=False)
    # print_credit_note = fields.Boolean(string='พิมพ์ใบลดหนี้/ใบกำกับภาษีแล้ว',copy=False)
    # print_debit_note = fields.Boolean(string='พิมพ์ใบเพิ่มหนี้/ใบกำกับภาษีแล้ว',copy=False)
    # debit_note = fields.Boolean(string='Debit Note', copy=False)
    # reference_later = fields.Boolean(string='Receive Tax Invoice Later',copy=False)
    ####################end ###############


    @api.depends('invoice_line_ids')
    def _get_tax_id(self):
        for inv in self:
            if inv.invoice_line_ids and inv.invoice_line_ids[0].invoice_line_tax_ids:
                inv.tax_id = inv.invoice_line_ids[0].invoice_line_tax_ids[0].id
                if not inv.tax_id.tax_report:
                    inv.tax_id = self.env['account.tax'].search([('type_tax_use','=','sale'),('tax_report','=',True)],limit=1)




    @api.depends('bill_date')
    def _get_string_date(self):
        for invoice in self:
            if invoice.bill_date:
                invoice.bill_date_str = str(strToDate(invoice.bill_date).strftime("%d/%m/%Y"))



    @api.multi
    def invoice_validate(self):
        if self.company_id.country_id.name == 'Thailand':
            for invoice in self.filtered(lambda invoice: invoice.partner_id not in invoice.message_partner_ids):
                if invoice.type in ('out_invoice', 'out_refund') and not invoice.partner_id.vat and not invoice.partner_id.customer_no_vat:
                    raise UserError(_("Invalid Customer TAX ID"))

                if not invoice.amount_total > 0.0:
                    raise UserError(_("Your Invoice Amount is 0"))

                if not invoice.reference and invoice.type == 'out_invoice':
                    invoice.reference = invoice._get_computed_reference()

                # DO NOT FORWARD-PORT.
                # The reference is copied after the move creation because we need the move to get the invoice number but
                # we need the invoice number to get the reference.
                invoice.move_id.ref = invoice.reference

                if invoice.type in ('in_invoice', 'in_refund'):
                    if invoice.reference:
                        if self.search([('type', '=', invoice.type), ('reference', '=', invoice.reference), ('company_id', '=', invoice.company_id.id), ('commercial_partner_id', '=', invoice.commercial_partner_id.id), ('id', '!=', invoice.id)]):
                            raise UserError(_("Duplicated vendor reference detected. You probably encoded twice the same vendor bill/refund."))
                    if not invoice.reference:
                        raise UserError(_(
                            "Please input vendor tax invoice number before validate"))

                if self.env.user.company_id.invoice_step == '1step':
                    self.write({'tax_inv_generated': True})

            self._check_duplicate_supplier_reference()
            return self.write({'state': 'open'})
        else:
            return super(AccountInvoice,self).invoice_validate()



    #return amount untax
    def get_tax_invoice(self):
        tax_invoice = self.env['account.invoice'].search([('number','=',self.origin)],limit=1)
        return tax_invoice.amount_untaxed

    # return invoice id
    def get_tax_invoice_id(self):
        tax_invoice = self.env['account.invoice'].search([('number', '=', self.origin)], limit=1)
        return tax_invoice

        # Load all unsold PO lines
    @api.onchange('purchase_id')
    def purchase_order_change(self):
        if not self.purchase_id:
            return {}
        if not self.partner_id:
            self.partner_id = self.purchase_id.partner_id.id
        new_lines = self.env['account.invoice.line']
        for line in self.purchase_id.order_line - self.invoice_line_ids.mapped('purchase_line_id'):
            data = self._prepare_invoice_line_from_po_line(line)
            new_line = new_lines.new(data)
            new_line._set_additional_fields(self)
            new_lines += new_line

        self.invoice_line_ids += new_lines
        self.purchase_id = False
        return {}

class AccountInvoiceTax(models.Model):
    _inherit = 'account.invoice.tax'

    partner_id = fields.Many2one('res.partner', string='Partner')
    ref = fields.Char(string='Sup Invoice No.')
