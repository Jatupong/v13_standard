# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import odoo.addons.decimal_precision as dp
from odoo import api, fields, models, _
from odoo.tools import float_is_zero, float_compare
from odoo.exceptions import UserError, ValidationError

class account_account(models.Model):
    _inherit = 'account.account'

    discount_account = fields.Boolean('Discount Account')



class account_move(models.Model):
    _inherit = 'account.move'

    is_line = fields.Boolean('Is a line')
    flag = fields.Boolean('flag')
    amount_tax_temp = fields.Float(string='Amount Tax Temp')

    def calc_discount(self):
        for move in self:
            # in case of create discount from invoice directly that mean first create invoice does not have Discount record
            discount_line_id = move.line_ids.filtered(lambda x: x.name == 'Discount')
            print ('-calc_discount')
            # print (discount_line_id)
            # if move.discount_apply_type == 'global' and not discount_line_id and move.discounted_amount:
            #     price = move.discounted_amount
            #     print('CREATE DISCOUNT LINE')
            #     if move.discount_account_id:
            #         discount_vals = {
            #             'account_id': move.discount_account_id,
            #             'quantity': 1,
            #             'price_unit': -price,
            #             'name': "Discount",
            #             'exclude_from_invoice_tab': True,
            #         }
            #         print (discount_vals)
            #         move.with_context(check_move_validity=False).write({
            #             'invoice_line_ids': [(0, 0, discount_vals)]
            #         })

    @api.depends('discount_apply_type','discount_value','discount_type')
    def _calculate_discount(self):
        res = discount = 0.0
        for self_obj in self:
            if self_obj.discount_apply_type == 'global':
                if self_obj.discount_type == 'Fixed':
                    res = self_obj.discount_value
                elif self_obj.discount_type == 'Percentage':
                    invoice_line_with_tax_ids = self_obj.invoice_line_ids.filtered(lambda x: x.tax_ids)

                    if invoice_line_with_tax_ids and invoice_line_with_tax_ids[0].tax_ids and invoice_line_with_tax_ids[0].tax_ids[
                        0].price_include and \
                            invoice_line_with_tax_ids[0].tax_ids[0].amount:
                        amount_total = 0.00
                        for line in self_obj.invoice_line_ids:
                            amount_total += line.price_total
                        print ('invoice amount total')
                        print (amount_total)
                        res = (amount_total) * (self_obj.discount_value / 100)
                    else:
                        res = self_obj.amount_untaxed * (self_obj.discount_value/ 100)
            else:
                res = discount

        print ('Return:')
        print (res)
        return res

    @api.depends(
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state','discount_type','discount_value')
    def _compute_amount(self):
        move_ids = [move.id for move in self if move.id and move.is_invoice(include_receipts=True)]
        self.env['account.payment'].flush(['state'])
        if move_ids:
            self._cr.execute(
                '''
                    SELECT move.id
                    FROM account_move move
                    JOIN account_move_line line ON line.move_id = move.id
                    JOIN account_partial_reconcile part ON part.debit_move_id = line.id OR part.credit_move_id = line.id
                    JOIN account_move_line rec_line ON
                        (rec_line.id = part.credit_move_id AND line.id = part.debit_move_id)
                        OR
                        (rec_line.id = part.debit_move_id AND line.id = part.credit_move_id)
                    JOIN account_payment payment ON payment.id = rec_line.payment_id
                    JOIN account_journal journal ON journal.id = rec_line.journal_id
                    WHERE payment.state IN ('posted', 'sent')
                    AND journal.post_at = 'bank_rec'
                    AND move.id IN %s
                ''', [tuple(move_ids)]
            )
            in_payment_set = set(res[0] for res in self._cr.fetchall())
        else:
            in_payment_set = {}

        for move in self:
            total_untaxed = 0.0
            total_untaxed_currency = 0.0
            total_tax = 0.0
            total_tax_currency = 0.0
            total_residual = 0.0
            total_residual_currency = 0.0
            total = 0.0
            total_currency = 0.0
            order_discount_tax = order_discount_untaxed = 0
            currencies = set()

            for line in move.line_ids:
                if line.currency_id:
                    currencies.add(line.currency_id)

                if move.is_invoice(include_receipts=True):
                    # === Invoices ===

                    if not line.exclude_from_invoice_tab:
                        # Untaxed amount.
                        print ('UNTAX--')
                        print (line.balance)
                        total_untaxed += line.balance
                        total_untaxed_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.tax_line_id:
                        # Tax amount.
                        total_tax += line.balance
                        total_tax_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.account_id.user_type_id.type in ('receivable', 'payable'):
                        # Residual amount.
                        total_residual += line.amount_residual
                        total_residual_currency += line.amount_residual_currency
                else:
                    # === Miscellaneous journal entry ===
                    if line.debit:
                        total += line.balance
                        total_currency += line.amount_currency

            if move.type == 'entry' or move.is_outbound():
                sign = 1
            else:
                sign = -1
            move.amount_untaxed = sign * (total_untaxed_currency if len(currencies) == 1 else total_untaxed)
            move.amount_tax = sign * (total_tax_currency if len(currencies) == 1 else total_tax)
            move.amount_total = sign * (total_currency if len(currencies) == 1 else total)
            move.amount_residual = -sign * (total_residual_currency if len(currencies) == 1 else total_residual)
            move.amount_untaxed_signed = -total_untaxed
            move.amount_tax_signed = -total_tax
            move.amount_total_signed = abs(total) if move.type == 'entry' else -total
            move.amount_residual_signed = total_residual
            res = move._calculate_discount()
            move.discounted_amount = res
            invoice_line_with_tax_ids = move.invoice_line_ids.filtered(lambda x: x.tax_ids)
            if move.invoice_line_ids and invoice_line_with_tax_ids and invoice_line_with_tax_ids[0].tax_ids[
                0].price_include and \
                    invoice_line_with_tax_ids[0].tax_ids[0].amount:
                print('-CASE-1')
                order_discount_tax = move.discounted_amount - move.discounted_amount / (
                        (100 + invoice_line_with_tax_ids[0].tax_ids[0].amount) * 0.01)
                order_discount_untaxed = move.discounted_amount / ((100 + invoice_line_with_tax_ids[0].tax_ids[0].amount) * 0.01)

                # move.amount_tax = move.amount_tax - order_discount_tax
                print (move.amount_total)
                print (order_discount_untaxed)
                print (order_discount_tax)
                print (move.discounted_amount)


                #OPTION-1, UPDATE UNTAX DISCOUNT
                move.amount_untaxed = move.amount_untaxed - order_discount_untaxed
                move.amount_total = move.amount_total + order_discount_tax - move.discounted_amount


            elif move.invoice_line_ids and invoice_line_with_tax_ids and not invoice_line_with_tax_ids[0].tax_ids[
                0].price_include and \
                    invoice_line_with_tax_ids[0].tax_ids[0].amount:

                print ('-CASE-2')
                order_discount_tax = move.discounted_amount * (invoice_line_with_tax_ids[0].tax_ids[0].amount * 0.01)
                order_discount_untaxed = move.discounted_amount

                # move.amount_tax = move.amount_tax - order_discount_tax
                print (move.amount_total)

                #OPTION-1, UPDATE UNTAX DISCOUNT
                move.amount_untaxed = move.amount_untaxed - order_discount_untaxed
                move.amount_total = move.amount_untaxed + move.amount_tax
            else:
                print('-CASE-3')
                order_discount_untaxed = move.discounted_amount
                move.amount_untaxed = move.amount_untaxed - order_discount_untaxed
                move.amount_total = move.amount_untaxed + move.amount_tax

            # print('--AMOUNT TOTAL')
            # print (move.amount_untaxed)
            # print (res)
            # print (order_discount_untaxed)
            # print (order_discount_tax)
            # print (move.amount_tax)
            # print (move.amount_total)

            currency = len(currencies) == 1 and currencies.pop() or move.company_id.currency_id
            is_paid = currency and currency.is_zero(move.amount_residual) or not move.amount_residual

            # Compute 'invoice_payment_state'.
            if move.type == 'entry':
                move.invoice_payment_state = False
            elif move.state == 'posted' and is_paid:
                if move.id in in_payment_set:
                    move.invoice_payment_state = 'in_payment'
                else:
                    move.invoice_payment_state = 'paid'
            else:
                move.invoice_payment_state = 'not_paid'

        # res_config= self.env['res.config.settings'].search([],order="id desc", limit=1)
        # print ('---RES CONFI')
        # print (res_config)
        if self.env.user.company_id.sale_account_id:
            for rec in self:
                if rec.discount_amt_line or rec.discounted_amount:
                    if rec.type == 'out_invoice':
                        if rec.company_id.sale_account_id:
                            rec.discount_account_id = rec.company_id.sale_account_id.id

                        else:
                            account_id = False
                            account_id = rec.env['account.account'].search([('user_type_id.name','=','Expenses'), ('discount_account','=',True)],limit=1)
                            if not account_id:
                                raise UserError(_('Please define an sale discount account for this company.'))
                            else:
                                rec.discount_account_id = account_id.id

                    if rec.type == 'in_invoice':
                        if rec.company_id.purchase_account_id:
                            rec.discount_account_id = rec.company_id.purchase_account_id.id
                        else:
                            account_id = False
                            account_id = rec.env['account.account'].search([('user_type_id.name','=','Income'), ('discount_account','=',True)],limit=1)
                            if not account_id:
                                raise UserError(_('Please define an purchase discount account for this company.'))
                            else:
                                rec.discount_account_id = account_id.id
        else:
            raise UserError(_('Please define an sale discount account for this company.'))

    tax_discount_policy = fields.Selection([('tax', 'Tax Amount'), ('untax', 'Untax Amount')],
                                           string='Discount Applies On', default='untax')
    discount_type = fields.Selection([('Fixed', 'Fixed'), ('Percentage', 'Percentage')],'Discount Method')
    discount_value = fields.Float('Discount Amount')
    discounted_amount = fields.Float(string='- Discount', readonly=True, compute='_compute_amount')
    amount_untaxed = fields.Float(string='Subtotal', digits=dp.get_precision('Account'),store=True, readonly=True, compute='_compute_amount',track_visibility='always')
    amount_tax = fields.Float(string='Tax', digits=dp.get_precision('Account'),store=True, readonly=True, compute='_compute_amount')
    amount_total = fields.Float(string='Total', digits=dp.get_precision('Account'),store=True, readonly=True, compute='_compute_amount')
    discount_apply_type = fields.Selection([('line', 'Order Line'), ('global', 'Global')], 'Discount Applies to',default='global')
    discount_account_id = fields.Many2one('account.account', 'Discount Account',compute='_compute_amount',store=True)
    discount_amt_line = fields.Float(compute='_compute_amount', string='- Line Discount', digits=dp.get_precision('Discount'), store=True, readonly=True)
    discount_amount_line = fields.Float(string="Discount Line")


    def _recompute_tax_lines(self, recompute_tax_base_amount=False):
        ''' Compute the dynamic tax lines of the journal entry.

        :param lines_map: The line_ids dispatched by type containing:
            * base_lines: The lines having a tax_ids set.
            * tax_lines: The lines having a tax_line_id set.
            * terms_lines: The lines generated by the payment terms of the invoice.
            * rounding_lines: The cash rounding lines of the invoice.
        '''

        print('_recompute_tax_lines')
        self.ensure_one()
        in_draft_mode = self != self._origin

        def _serialize_tax_grouping_key(grouping_dict):
            ''' Serialize the dictionary values to be used in the taxes_map.
            :param grouping_dict: The values returned by '_get_tax_grouping_key_from_tax_line' or '_get_tax_grouping_key_from_base_line'.
            :return: A string representing the values.
            '''
            return '-'.join(str(v) for v in grouping_dict.values())

        def _compute_base_line_taxes(base_line):
            ''' Compute taxes amounts both in company currency / foreign currency as the ratio between
            amount_currency & balance could not be the same as the expected currency rate.
            The 'amount_currency' value will be set on compute_all(...)['taxes'] in multi-currency.
            :param base_line:   The account.move.line owning the taxes.
            :return:            The result of the compute_all method.
            '''
            move = base_line.move_id

            if move.is_invoice(include_receipts=True):
                handle_price_include = True
                sign = -1 if move.is_inbound() else 1
                quantity = base_line.quantity
                if base_line.currency_id:
                    price_unit_foreign_curr = sign * base_line.price_unit * (1 - (base_line.discount / 100.0))
                    price_unit_comp_curr = base_line.currency_id._convert(price_unit_foreign_curr,
                                                                          move.company_id.currency_id, move.company_id,
                                                                          move.date, round=False)
                else:
                    price_unit_foreign_curr = 0.0
                    price_unit_comp_curr = sign * base_line.price_unit * (1 - (base_line.discount / 100.0))
                tax_type = 'sale' if move.type.startswith('out_') else 'purchase'
                is_refund = move.type in ('out_refund', 'in_refund')
            else:
                handle_price_include = False
                quantity = 1.0
                price_unit_foreign_curr = base_line.amount_currency
                price_unit_comp_curr = base_line.balance
                tax_type = base_line.tax_ids[0].type_tax_use if base_line.tax_ids else None
                is_refund = (tax_type == 'sale' and base_line.debit) or (tax_type == 'purchase' and base_line.credit)

            # res_config = self.env['res.config.settings'].search([], order="id desc", limit=1)
            # if res_config:
            #     for rec in self:
            #         if res_config.tax_discount_policy == 'untax':
            #             quantity = 1.0
            #             if rec.discount_apply_type == 'line':
            #                 if base_line.discount_type == 'fix':
            #                     price_unit_comp_curr = base_line.price_subtotal - base_line.discount_amount
            #                 elif base_line.discount_type == 'Percentage':
            #                     price_unit_comp_curr = base_line.price_subtotal * (1 - (base_line.discount_amount / 100.0))
            #
            #             elif rec.discount_apply_type == 'global':
            #                 if rec.amount_untaxed != 0.0:
            #                     # print ('---Untax != 0')
            #                     final_discount = ((rec.discounted_amount * base_line.price_subtotal) / rec.amount_untaxed)
            #                     price_unit_comp_curr = base_line.price_subtotal - rec.currency_id.round(final_discount)
            #                     # print (final_discount)
            #                     # print (price_unit_comp_curr)
            #                 else:
            #                     final_discount = (rec.discounted_amount * base_line.price_subtotal) / 1.0
            #                     discount = base_line.price_subtotal - rec.currency_id.round(final_discount)
            #         else:
            #             if self._context.get('default_type') in ('out_invoice', 'out_refund', 'out_receipt'):
            #                 sign = -(sign)
            #             else:
            #                 pass
            #     price_unit_comp_curr = sign * price_unit_comp_curr

            balance_taxes_res = base_line.tax_ids._origin.with_context(
                force_sign=move._get_tax_force_sign()).compute_all(
                price_unit_comp_curr,
                currency=base_line.company_currency_id,
                quantity=quantity,
                product=base_line.product_id,
                partner=base_line.partner_id,
                is_refund=is_refund,
                handle_price_include=handle_price_include,
            )

            if move.type == 'entry':
                repartition_field = is_refund and 'refund_repartition_line_ids' or 'invoice_repartition_line_ids'
                repartition_tags = base_line.tax_ids.flatten_taxes_hierarchy().mapped(repartition_field).filtered(
                    lambda x: x.repartition_type == 'base').tag_ids
                tags_need_inversion = (tax_type == 'sale' and not is_refund) or (tax_type == 'purchase' and is_refund)
                if tags_need_inversion:
                    balance_taxes_res['base_tags'] = base_line._revert_signed_tags(repartition_tags).ids
                    for tax_res in balance_taxes_res['taxes']:
                        tax_res['tag_ids'] = base_line._revert_signed_tags(
                            self.env['account.account.tag'].browse(tax_res['tag_ids'])).ids

            if base_line.currency_id:
                # Multi-currencies mode: Taxes are computed both in company's currency / foreign currency.
                amount_currency_taxes_res = base_line.tax_ids._origin.with_context(
                    force_sign=move._get_tax_force_sign()).compute_all(
                    price_unit_foreign_curr,
                    currency=base_line.currency_id,
                    quantity=quantity,
                    product=base_line.product_id,
                    partner=base_line.partner_id,
                    is_refund=self.type in ('out_refund', 'in_refund'),
                    handle_price_include=handle_price_include,
                )

                if move.type == 'entry':
                    repartition_field = is_refund and 'refund_repartition_line_ids' or 'invoice_repartition_line_ids'
                    repartition_tags = base_line.tax_ids.mapped(repartition_field).filtered(
                        lambda x: x.repartition_type == 'base').tag_ids
                    tags_need_inversion = (tax_type == 'sale' and not is_refund) or (
                            tax_type == 'purchase' and is_refund)
                    if tags_need_inversion:
                        balance_taxes_res['base_tags'] = base_line._revert_signed_tags(repartition_tags).ids
                        for tax_res in balance_taxes_res['taxes']:
                            tax_res['tag_ids'] = base_line._revert_signed_tags(
                                self.env['account.account.tag'].browse(tax_res['tag_ids'])).ids

                for b_tax_res, ac_tax_res in zip(balance_taxes_res['taxes'], amount_currency_taxes_res['taxes']):
                    tax = self.env['account.tax'].browse(b_tax_res['id'])
                    b_tax_res['amount_currency'] = ac_tax_res['amount']

                    # A tax having a fixed amount must be converted into the company currency when dealing with a
                    # foreign currency.
                    if tax.amount_type == 'fixed':
                        b_tax_res['amount'] = base_line.currency_id._convert(b_tax_res['amount'],
                                                                             move.company_id.currency_id,
                                                                             move.company_id,
                                                                             move.date)
            print(balance_taxes_res)
            return balance_taxes_res

        taxes_map = {}

        # ==== Add tax lines ====
        to_remove = self.env['account.move.line']
        for line in self.line_ids.filtered('tax_repartition_line_id'):
            grouping_dict = self._get_tax_grouping_key_from_tax_line(line)
            grouping_key = _serialize_tax_grouping_key(grouping_dict)
            if grouping_key in taxes_map:
                # A line with the same key does already exist, we only need one
                # to modify it; we have to drop this one.
                to_remove += line
            else:
                taxes_map[grouping_key] = {
                    'tax_line': line,
                    'balance': 0.0,
                    'amount_currency': 0.0,
                    'tax_base_amount': 0.0,
                    'grouping_dict': False,
                }
        if not recompute_tax_base_amount:
            self.line_ids -= to_remove

        # ==== Mount base lines ====
        for line in self.line_ids.filtered(lambda line: not line.tax_repartition_line_id):
            # Don't call compute_all if there is no tax.
            if not line.tax_ids:
                if not recompute_tax_base_amount:
                    line.tag_ids = [(5, 0, 0)]
                continue

            compute_all_vals = _compute_base_line_taxes(line)

            # Assign tags on base line
            if not recompute_tax_base_amount:
                line.tag_ids = compute_all_vals['base_tags'] or [(5, 0, 0)]

            tax_exigible = True
            for tax_vals in compute_all_vals['taxes']:
                grouping_dict = self._get_tax_grouping_key_from_base_line(line, tax_vals)
                grouping_key = _serialize_tax_grouping_key(grouping_dict)

                tax_repartition_line = self.env['account.tax.repartition.line'].browse(
                    tax_vals['tax_repartition_line_id'])
                tax = tax_repartition_line.invoice_tax_id or tax_repartition_line.refund_tax_id

                if tax.tax_exigibility == 'on_payment':
                    tax_exigible = False

                taxes_map_entry = taxes_map.setdefault(grouping_key, {
                    'tax_line': None,
                    'balance': 0.0,
                    'amount_currency': 0.0,
                    'tax_base_amount': 0.0,
                    'grouping_dict': False,
                })
                taxes_map_entry['balance'] += tax_vals['amount']
                taxes_map_entry['amount_currency'] += tax_vals.get('amount_currency', 0.0)
                taxes_map_entry['tax_base_amount'] += self._get_base_amount_to_display(tax_vals['base'],
                                                                                       tax_repartition_line,
                                                                                       tax_vals['group'])
                taxes_map_entry['grouping_dict'] = grouping_dict
            if not recompute_tax_base_amount:
                line.tax_exigible = tax_exigible

        # ==== Process taxes_map ====
        print('--taxes_map.values()')
        print(taxes_map.values())
        for taxes_map_entry in taxes_map.values():
            # Don't create tax lines with zero balance.
            if self.currency_id.is_zero(taxes_map_entry['balance']) and self.currency_id.is_zero(
                    taxes_map_entry['amount_currency']):
                taxes_map_entry['grouping_dict'] = False

            tax_line = taxes_map_entry['tax_line']
            tax_base_amount = -taxes_map_entry['tax_base_amount'] if self.is_inbound() else taxes_map_entry[
                'tax_base_amount']
            # balance = -taxes_map_entry['balance'] if self.is_inbound() else taxes_map_entry[
            #     'balance']
            #********************************************additional code by JA########################
            if self.type == 'out_invoice':
                print('---out_invoice')
                invoice_line_with_tax_ids = self.invoice_line_ids.filtered(lambda x: x.tax_ids)
                if self.invoice_line_ids and invoice_line_with_tax_ids and invoice_line_with_tax_ids[0].tax_ids[
                    0].price_include and \
                        invoice_line_with_tax_ids[0].tax_ids[0].amount:

                    print ('---UPDATE DISCOUN IN TAX')
                    discount_amount = self._calculate_discount()
                    tax_base_amount = tax_base_amount - discount_amount/(1.07)
                    taxes_map_entry['balance'] = taxes_map_entry['balance'] + (discount_amount - discount_amount/(1.07))
                elif self.invoice_line_ids and invoice_line_with_tax_ids and not invoice_line_with_tax_ids[0].tax_ids[
                    0].price_include and \
                        invoice_line_with_tax_ids[0].tax_ids[0].amount:
                    # print('---UPDATE DISCOUN EX TAX')
                    print(taxes_map_entry)
                    discount_amount = self._calculate_discount()
                    tax_base_amount = tax_base_amount - discount_amount
                    taxes_map_entry['balance'] = taxes_map_entry['balance'] + (self.discounted_amount*0.07)
                    print (taxes_map_entry)
                    print ('--END-tAX COMPUTER')
                else:
                    print ('--NOT UPDATE DISCOUNT')
            elif self.type == 'in_invoice':
                print (tax_base_amount)
                invoice_line_with_tax_ids = self.invoice_line_ids.filtered(lambda x: x.tax_ids)
                if self.invoice_line_ids and invoice_line_with_tax_ids and invoice_line_with_tax_ids[0].tax_ids[
                    0].price_include and \
                        invoice_line_with_tax_ids[0].tax_ids[0].amount:

                    discount_amount = self._calculate_discount()
                    tax_base_amount = tax_base_amount - discount_amount / (1.07)
                    taxes_map_entry['balance'] = taxes_map_entry['balance'] - (
                            discount_amount - discount_amount / (1.07))
                elif self.invoice_line_ids and invoice_line_with_tax_ids and not \
                        invoice_line_with_tax_ids[0].tax_ids[
                            0].price_include and \
                        invoice_line_with_tax_ids[0].tax_ids[0].amount:
                    discount_amount = self._calculate_discount()
                    tax_base_amount = tax_base_amount - discount_amount
                    taxes_map_entry['balance'] = taxes_map_entry['balance'] - (self.discounted_amount * 0.07)
            # ********************************************#

            print ('--taxes_map_entry--')
            print (taxes_map_entry)
            if not tax_line and not taxes_map_entry['grouping_dict']:
                continue
            elif tax_line and recompute_tax_base_amount:
                tax_line.tax_base_amount = tax_base_amount
            elif tax_line and not taxes_map_entry['grouping_dict']:
                # The tax line is no longer used, drop it.
                self.line_ids -= tax_line
            elif tax_line:
                tax_line.update({
                    'amount_currency': taxes_map_entry['amount_currency'],
                    'debit': taxes_map_entry['balance'] > 0.0 and taxes_map_entry['balance'] or 0.0,
                    'credit': taxes_map_entry['balance'] < 0.0 and -taxes_map_entry['balance'] or 0.0,
                    'tax_base_amount': tax_base_amount,
                })
            else:
                create_method = in_draft_mode and self.env['account.move.line'].new or self.env[
                    'account.move.line'].create
                tax_repartition_line_id = taxes_map_entry['grouping_dict']['tax_repartition_line_id']
                tax_repartition_line = self.env['account.tax.repartition.line'].browse(tax_repartition_line_id)
                tax = tax_repartition_line.invoice_tax_id or tax_repartition_line.refund_tax_id
                tax_line = create_method({
                    'name': tax.name,
                    'move_id': self.id,
                    'partner_id': line.partner_id.id,
                    'company_id': line.company_id.id,
                    'company_currency_id': line.company_currency_id.id,
                    'quantity': 1.0,
                    'date_maturity': False,
                    'amount_currency': taxes_map_entry['amount_currency'],
                    'debit': taxes_map_entry['balance'] > 0.0 and taxes_map_entry['balance'] or 0.0,
                    'credit': taxes_map_entry['balance'] < 0.0 and -taxes_map_entry['balance'] or 0.0,
                    'tax_base_amount': tax_base_amount,
                    'exclude_from_invoice_tab': True,
                    'tax_exigible': tax.tax_exigibility == 'on_invoice',
                    **taxes_map_entry['grouping_dict'],
                })

            if tax_line and in_draft_mode:
                tax_line._onchange_amount_currency()
                tax_line._onchange_balance()

        print('--taxes_map.values()')
        print(taxes_map.values())

    @api.model_create_multi
    def create(self, vals_list):
        res = super(account_move,self).create(vals_list)
        for val in vals_list:
            if 'flag' in val and not self._context.get('default_type') == 'in_invoice' :
                val.pop('flag')

            else:
                name = False
                for line in res.line_ids:
                    name = line.name
                # if res.discount_apply_type == 'line':
                #     price = res.discount_amt_line
                for move in res:
                    if move.discount_apply_type == 'global':
                        price = move.discounted_amount
                    else:
                        price = 0
                    if name != 'Discount':
                        if move.discount_account_id:
                            discount_vals = {
                                'account_id': move.discount_account_id,
                                'quantity': 1,
                                'price_unit': -price,
                                'name': "Discount",
                                'exclude_from_invoice_tab': True,
                            }
                            move.with_context(check_move_validity=False).write({
                                'invoice_line_ids' : [(0,0,discount_vals)]
                            })
                        else:
                            pass

        # print("CREATE--")
        # print(res)
        # print(vals_list)
        return res

    @api.onchange('invoice_line_ids','discount_amount','discount_apply_type')
    def _onchange_invoice_line_ids(self):
        print ('_onchange_invoice_line_ids----')
        current_invoice_lines = self.line_ids.filtered(lambda line: not line.exclude_from_invoice_tab)
        others_lines = self.line_ids - current_invoice_lines
        if others_lines and current_invoice_lines - self.invoice_line_ids:
            others_lines[0].recompute_tax_line = True
        self.line_ids = others_lines + self.invoice_line_ids
        self._onchange_recompute_dynamic_lines()
        # if self._context.get('default_type') == 'out_invoice' :
        #     total = 0.0
        #     for line in self.invoice_line_ids:
        #         if line.discount_type == 'Percentage':
        #             total += line.price_unit * (line.discount_amount/ 100)
        #         elif line.discount_type == 'Fixed':
        #             total += line.discount_amount
        #     self.discount_amount_line = total

    @api.onchange('invoice_vendor_bill_id')
    def _onchange_invoice_vendor_bill(self):
        print ('--_onchange_invoice_vendor_bill--')
        if self.invoice_vendor_bill_id:
            # Copy invoice lines.
            for line in self.invoice_vendor_bill_id.invoice_line_ids:
                copied_vals = line.copy_data()[0]
                copied_vals['move_id'] = self.id
                new_line = self.env['account.move.line'].new(copied_vals)
                new_line.recompute_tax_line = True

            # Copy payment terms.
            self.invoice_payment_term_id = self.invoice_vendor_bill_id.invoice_payment_term_id

            # Copy currency.
            if self.currency_id != self.invoice_vendor_bill_id.currency_id:
                self.currency_id = self.invoice_vendor_bill_id.currency_id

            # Reset
            self.invoice_vendor_bill_id = False
            self._recompute_dynamic_lines()


    def update_discount_currency(self):
        # print ('--UPDATe--')
        sum_credit = sum_debit = 0
        for aml in self.line_ids:
            sum_debit += aml.debit
            sum_credit += aml.credit

        if float_compare(sum_debit,sum_credit,precision_digits=2) != 0:
            # print ('--COMPARE')
            discount_line = self.line_ids.filtered(lambda x: x.name == "Discount")
            if discount_line.credit:
                new_value = discount_line.credit
                new_value += sum_debit - sum_credit
                discount_line.write({'credit': new_value})

            elif discount_line.debit:
                new_value = discount_line.debit
                new_value -= sum_debit - sum_credit
                discount_line.write({'debit': new_value})


    # def apply_discount_direct(self):
        # for move in self:
        #     # in case of create discount from invoice directly that mean first create invoice does not have Discount record
        #     discount_line_id = move.line_ids.filtered(lambda x: x.name == 'Discount')
        #     if move.discount_apply_type == 'global' and not discount_line_id and move.discounted_amount:
        #         price = move.discounted_amount
        #         print('CREATE DISCOUNT LINE')
        #         if move.discount_account_id:
        #             discount_vals = {
        #                 'account_id': move.discount_account_id,
        #                 'quantity': 1,
        #                 'price_unit': -price,
        #                 'name': "Discount",
        #                 'exclude_from_invoice_tab': True,
        #             }
        #             move.with_context(check_move_validity=False).write({
        #                 'invoice_line_ids': [(0, 0, discount_vals)]
        #             })

    @api.depends('discount_value','discount_type')
    def write(self,vals):
        res = super(account_move,self).write(vals)
        for move in self:
            print ('--ST1')
            found_discount = False
            for rec in move.line_ids:
                print('--ST2')
                if move.discount_apply_type != 'line':
                    print('--ST3')
                    if rec.name == "Discount":
                        found_discount = True
                        invoice_line_with_tax_ids = move.invoice_line_ids.filtered(lambda x: x.tax_ids)
                        if move.invoice_line_ids and invoice_line_with_tax_ids and invoice_line_with_tax_ids[0].tax_ids[
                            0].price_include and \
                                invoice_line_with_tax_ids[0].tax_ids[0].amount:


                            if move.currency_id != self.env.user.company_id.currency_id:
                                discounted_amount = move.currency_id._convert(move.discounted_amount,
                                                                         move.company_id.currency_id,
                                                                         move.company_id,
                                                                         move.date)


                                rec.with_context(check_move_validity=False).write(
                                    {'price_unit': discounted_amount *(-1) / 1.07})
                            else:
                                rec.with_context(check_move_validity=False).write({'price_unit': -move.discounted_amount/1.07})
                        else:
                            if move.currency_id != self.env.user.company_id.currency_id:
                                discounted_amount = move.currency_id._convert(move.discounted_amount,
                                                                         move.company_id.currency_id,
                                                                         move.company_id,
                                                                         move.date)
                                rec.with_context(check_move_validity=False).write({'price_unit': discounted_amount*(-1)})

                            else:
                                rec.with_context(check_move_validity=False).write({'price_unit':-move.discounted_amount})


                if self._context.get('default_type') == 'in_invoice' :
                    if rec.name == False or rec.name == '':
                        if move.discounted_amount:
                            if move.currency_id != self.env.user.company_id.currency_id:
                                total_amount = move.currency_id._convert(move.amount_total,
                                                                         move.company_id.currency_id,
                                                                         move.company_id,
                                                                         move.date)
                                rec.with_context(check_move_validity=False).write({'credit': total_amount})

                            else:
                                rec.with_context(check_move_validity=False).write({'credit':move.amount_total})


                    # if self.invoice_line_ids and self.invoice_line_ids[0].tax_ids and self.invoice_line_ids[0].tax_ids[
                    #     0].price_include and \
                    #         self.invoice_line_ids[0].tax_ids[0].amount and rec.name == self.invoice_line_ids[0].tax_ids[
                    #     0].name:
                    #     rec.with_context(check_move_validity=False).write({'debit': self.amount_tax})

                    if move.discount_apply_type == 'line':
                        if rec.name == "Discount":
                            rec.with_context(check_move_validity=False).write({'credit':move.discount_amt_line})

                if self._context.get('default_type') == 'out_invoice' :
                    amount_total = move.amount_tax + move.amount_untaxed - move.discount_amount_line

                    if move.discount_apply_type == 'line':
                        if rec.name == "Discount":
                            if move.discount_amount_line > 0.0:
                                rec.with_context(check_move_validity=False).write({'debit':move.discount_amount_line})
                                rec.with_context(check_move_validity=False).write({'credit':0.0})
                        if rec.name == False or rec.name == '':
                            if move.discount_value_line > 0.0:
                                rec.with_context(check_move_validity=False).write({'debit':amount_total})
                    else:
                        if rec.name == False or rec.name == '':
                            if move.discounted_amount:
                                if move.currency_id != self.env.user.company_id.currency_id:
                                    total_amount = move.currency_id._convert(move.amount_total,
                                                         move.company_id.currency_id,
                                                         move.company_id,
                                                         move.date)
                                    rec.with_context(check_move_validity=False).write({'debit': total_amount})
                                else:
                                    rec.with_context(check_move_validity=False).write({'debit':move.amount_total})
                        # if self.invoice_line_ids and self.invoice_line_ids[0].tax_ids and self.invoice_line_ids[0].tax_ids[
                        #     0].price_include and \
                        #         self.invoice_line_ids[0].tax_ids[0].amount and rec.name == self.invoice_line_ids[0].tax_ids[0].name:
                        #     rec.with_context(check_move_validity=False).write({'credit':self.amount_tax})

                else:
                    pass

            if move.currency_id != self.env.user.company_id.currency_id:
                move.update_discount_currency()

        return res
    @api.onchange('discount_value','discount_type')
    def _onchange_taxes(self):
        ''' Recompute the dynamic onchange based on taxes.
        If the edited line is a tax line, don't recompute anything as the user must be able to
        set a custom value.
        '''
        # print ('_onchange_taxes')
        self._recompute_tax_lines()
        for line in self.line_ids:
            if not line.tax_repartition_line_id:
                line.recompute_tax_line = True

class account_payment(models.Model):
    _inherit = "account.payment"

    def _prepare_payment_moves(self):

        res = super(account_payment,self)._prepare_payment_moves()
        for rec in res:
            rec.update({'flag':True})
        return res

#
# class account_move_line(models.Model):
#     _inherit = 'account.move.line'

# discount_type = fields.Selection([('Fixed', 'Fixed'), ('Percentage', 'Percentage')], 'Discount Method')
# discount_apply_type = fields.Selection(related='move_id.discount_apply_type', string="Discount Applies to")
# discount_amount = fields.Float('Discount Amount')
# discount_amt = fields.Float('Discount Final Amount')

# @api.onchange('discount_type','discount_amount','amount_currency', 'currency_id', 'debit', 'credit', 'tax_ids', 'account_id',)
# def _onchange_mark_recompute_taxes(self):
#     ''' Recompute the dynamic onchange based on taxes.
#     If the edited line is a tax line, don't recompute anything as the user must be able to
#     set a custom value.
#     '''
#     for line in self:
#         if not line.tax_repartition_line_id:
#             line.recompute_tax_line = True

