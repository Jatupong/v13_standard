# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import odoo.addons.decimal_precision as dp
from odoo import api, fields, models, _

class purchase_order(models.Model):
    _inherit = 'purchase.order'
    

    @api.depends('order_line','order_line.price_total','order_line.price_subtotal',\
        'order_line.product_qty','discount_value',\
        'discount_apply_type','discount_type')
    # @api.depends('order_line', 'order_line.price_total', 'order_line.price_subtotal', \
    #              'order_line.product_qty', 'discount_value', \
    #              'discount_apply_type', 'discount_type', 'order_line.discount_amount', \
    #              'order_line.discount_apply_type')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        res_config= self.env['res.config.settings'].search([],order="id desc", limit=1)
        cur_obj = self.env['res.currency']
        for order in self:
            applied_discount = line_discount = sums = order_discount =  amount_untaxed = amount_none_taxed = amount_tax  = 0.0
            for line in order.order_line:
                # amount_untaxed += line.price_subtotal
                # amount_tax += line.price_tax
                if line.taxes_id:
                    amount_untaxed += line.price_subtotal
                else:
                    amount_none_taxed += line.price_subtotal

                amount_tax += line.price_tax

                # applied_discount += line.discount_amt
                # if line.discount_type == 'Fixed':
                #     line_discount += line.discount_amount
                # elif line.discount_type == 'Percentage':
                #     line_discount += line.price_subtotal * (line.discount_amount/ 100)
            if order:
                if order.tax_discount_policy == 'tax':
                    if order.discount_apply_type == 'line':
                        order.discounted_amount = 0.00
                        # order.update({
                        #     'amount_untaxed': amount_untaxed,
                        #     'amount_tax': amount_tax,
                        #     'amount_total': amount_untaxed + amount_tax - line_discount,
                        #     'discount_amt_line' : line_discount,
                        # })
                    elif order.discount_apply_type == 'global':
                        order.discount_amt_line = 0.00
                        if order.discount_type == 'Percentage':
                            order_discount = amount_untaxed*(order.discount_value / 100)
                            order.update({
                                'amount_untaxed': amount_untaxed,
                                'amount_tax': amount_tax,
                                'amount_total': amount_untaxed + amount_tax - order_discount,
                                'discounted_amount' : order_discount,
                            })
                        elif order.discount_type == 'Fixed':
                            order_discount = order.discount_value
                            order.update({
                                'amount_untaxed': amount_untaxed,
                                'amount_tax': amount_tax,
                                'amount_total': amount_untaxed + amount_tax - order_discount,
                                'discounted_amount' : order_discount,
                            })
                        else:
                            order.update({
                                'amount_untaxed': amount_untaxed,
                                'amount_tax': amount_tax,
                                'amount_total': amount_untaxed + amount_tax ,
                            })
                    else:
                        order.update({
                            'amount_untaxed': amount_untaxed,
                            'amount_tax': amount_tax,
                            'amount_total': amount_untaxed + amount_tax ,
                            })
                elif order.tax_discount_policy == 'untax':
                    if order.discount_apply_type == 'line':
                        order.discounted_amount = 0.00
                        # for line in order.order_line:
                        #     if line.discount_type == 'Fixed' and line.taxes_id.price_include == True:
                        #         price_amount = amount_untaxed - line.discount_amount
                        #         taxes = line.taxes_id.compute_all(price_amount, line.order_id.currency_id, 1, product=line.product_id, partner=order.partner_id)
                        #         sums += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
                        #     elif line.discount_type == 'Percentage' and line.taxes_id.price_include == True:
                        #         price_amount = line.price_subtotal - ((line.discount_amount*line.price_subtotal)/100.0)
                        #         taxes = line.taxes_id.compute_all(price_amount, line.order_id.currency_id, 1, product=line.product_id, partner=order.partner_id)
                        #         sums += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
                        #     elif line.discount_type == 'Fixed' and not line.taxes_id.price_include == True:
                        #         sums = amount_tax
                        #     elif line.discount_type == 'Percentage' and not line.taxes_id.price_include == True:
                        #         sums = amount_tax
                        # order.update({
                        #     'amount_untaxed': amount_untaxed,
                        #     'amount_tax': sums,
                        #     'amount_total': amount_untaxed + sums - applied_discount,
                        #     'discount_amt_line' : applied_discount,
                        # })
                    elif order.discount_apply_type == 'global':
                        order.discount_amt_line = 0.00
                        order_line_taxes_ids = order.order_line.filtered(lambda x: x.taxes_id)
                        if order.discount_type == 'Percentage':
                            if order_line_taxes_ids and order_line_taxes_ids[0].taxes_id and order.order_line[0].taxes_id[
                                0].price_include:
                                order_discount = (amount_untaxed + amount_none_taxed + amount_tax) * (order.discount_value / 100)
                            else:
                                order_discount = (amount_untaxed + amount_none_taxed) * (order.discount_value / 100)

                            if order_line_taxes_ids and order_line_taxes_ids[0].taxes_id and order.order_line[0].taxes_id[
                                0].price_include and \
                                    order_line_taxes_ids[0].taxes_id[0].amount:
                                order_discount_tax = order_discount - order_discount/((100 + order_line_taxes_ids[0].taxes_id[0].amount) * 0.01)
                                order_discount_untaxed = order_discount/((100 + order_line_taxes_ids[0].taxes_id[0].amount) * 0.01)

                            elif order_line_taxes_ids and order_line_taxes_ids[0].taxes_id and not order_line_taxes_ids[0].taxes_id[
                                    0].price_include and \
                                        order_line_taxes_ids[0].taxes_id[0].amount:
                                order_discount_tax = order_discount*(order_line_taxes_ids[0].taxes_id[0].amount) * 0.01
                                order_discount_untaxed = order_discount
                            else:
                                order_discount_tax = 0.00
                                order_discount_untaxed = order_discount

                            # order.update({
                            #     'amount_untaxed': amount_untaxed - order_discount_untaxed,
                            #     'amount_tax': amount_tax - order_discount_tax,
                            #     'amount_total': amount_untaxed + amount_tax - order_discount_tax - order_discount_untaxed,
                            #     'discounted_amount': order_discount,
                            # })
                            amount_total = amount_untaxed + amount_none_taxed + amount_tax - order_discount_tax - order_discount_untaxed
                            if not amount_none_taxed and amount_tax:
                                print ('CASE=P-1')
                                order.update({
                                    'amount_total': amount_untaxed + amount_tax - order_discount_tax - order_discount_untaxed,
                                    'amount_untaxed': amount_total / 1.07,
                                    'amount_tax': amount_total - amount_total / 1.07,
                                    'discounted_amount': order_discount,
                                })
                            elif amount_none_taxed and amount_tax:
                                print('CASE=P-2')
                                amount_total_tax = amount_untaxed + amount_tax - order_discount
                                amount_untaxed_new = amount_total_tax / 1.07
                                amount_tax_new = amount_total_tax - amount_untaxed_new
                                order.update({
                                    'amount_untaxed': amount_untaxed_new + amount_none_taxed,
                                    'amount_tax': amount_tax_new,
                                    'amount_total': amount_total,
                                    'discounted_amount': order_discount,
                                })
                            else:
                                print('CASE=P-3')
                                amount_total_tax = amount_untaxed + amount_none_taxed + amount_tax - order_discount
                                # amount_untaxed_new = amount_total_tax / 1.07
                                # amount_tax_new = amount_total_tax - amount_untaxed_new
                                print (order_discount)
                                order.update({
                                    'amount_untaxed': amount_total_tax,
                                    'amount_tax': amount_tax,
                                    'amount_total': amount_total_tax,
                                    'discounted_amount': order_discount,
                                })

                        elif order.discount_type == 'Fixed':
                            order_discount = order.discount_value
                            # print ('FIX DISCOUNT')
                            # print (order_discount)

                            if order_line_taxes_ids and order_line_taxes_ids[0].taxes_id and order_line_taxes_ids[0].taxes_id[
                                0].price_include and \
                                    order.order_line[0].taxes_id[0].amount:
                                order_discount_tax = order_discount - order_discount/((100 + order.order_line[0].taxes_id[0].amount) * 0.01)
                                order_discount_untaxed = order_discount/((100 + order.order_line[0].taxes_id[0].amount) * 0.01)
                            elif order_line_taxes_ids and order_line_taxes_ids[0].taxes_id and not order_line_taxes_ids[0].taxes_id[
                                    0].price_include and \
                                        order_line_taxes_ids[0].taxes_id[0].amount:
                                order_discount_tax = order_discount*((order_line_taxes_ids[0].taxes_id[0].amount) * 0.01)
                                order_discount_untaxed = order_discount
                            else:
                                order_discount_tax = 0
                                order_discount_untaxed = order_discount

                            # order.update({
                            #     'amount_untaxed': amount_untaxed - order_discount_untaxed,
                            #     'amount_tax': amount_tax - order_discount_tax,
                            #     'amount_total': amount_untaxed + amount_tax - order_discount_tax - order_discount_untaxed,
                            #     'discounted_amount': order_discount,
                            # })
                            amount_total = amount_untaxed + amount_none_taxed + amount_tax - order_discount_tax - order_discount_untaxed
                            if not amount_none_taxed and amount_tax:
                                print ('--CASE-f-1')
                                order.update({
                                    'amount_total': amount_untaxed + amount_tax - order_discount_tax - order_discount_untaxed,
                                    'amount_untaxed': amount_total / 1.07,
                                    'amount_tax': amount_total - amount_total / 1.07,
                                    'discounted_amount': order_discount,
                                })
                            elif amount_none_taxed and amount_tax:
                                print('--CASE-f-2')
                                amount_total_tax = amount_untaxed + amount_tax - order_discount
                                amount_untaxed_new = amount_total_tax / 1.07
                                amount_tax_new = amount_total_tax - amount_untaxed_new
                                order.update({
                                    'amount_untaxed': amount_untaxed_new + amount_none_taxed,
                                    'amount_tax': amount_tax_new,
                                    'amount_total': amount_total,
                                    'discounted_amount': order_discount,
                                })
                            #not amount_tax
                            else:
                                print('--CASE-f-3')
                                amount_total_tax = amount_untaxed + amount_none_taxed + amount_tax - order_discount
                                # amount_untaxed_new = amount_total_tax / 1.07
                                # amount_tax_new = amount_total_tax - amount_untaxed_new
                                order.update({
                                    'amount_untaxed': amount_total_tax,
                                    'amount_tax': amount_tax,
                                    'amount_total': amount_total_tax,
                                    'discounted_amount': order_discount,
                                })
                        else:
                            # order.update({
                            #     'amount_untaxed': amount_untaxed,
                            #     'amount_tax': amount_tax,
                            #     'amount_total': amount_untaxed + amount_tax ,
                            # })
                            amount_total = amount_untaxed + amount_none_taxed + amount_tax
                            if not amount_none_taxed:
                                order.update({
                                    'amount_untaxed': amount_total / 1.07,
                                    'amount_tax': amount_total - amount_total / 1.07,
                                    'amount_total': amount_total,
                                })
                            else:
                                amount_total_tax = amount_untaxed + amount_tax
                                amount_untaxed_new = amount_total_tax / 1.07
                                amount_tax_new = amount_total_tax - amount_untaxed_new
                                order.update({
                                    'amount_untaxed': amount_untaxed_new + amount_none_taxed,
                                    'amount_tax': amount_tax_new,
                                    'amount_total': amount_untaxed + amount_none_taxed + amount_tax - order_discount,
                                    'discounted_amount': order_discount,
                                })
                    else:
                        # order.update({
                        #     'amount_untaxed': amount_untaxed,
                        #     'amount_tax': amount_tax,
                        #     'amount_total': amount_untaxed + amount_tax ,
                        #     })
                        amount_total = amount_untaxed + amount_none_taxed + amount_tax
                        if not amount_none_taxed:
                            order.update({
                                'amount_untaxed': amount_total / 1.07,
                                'amount_tax': amount_total - amount_total / 1.07,
                                'amount_total': amount_total,
                            })
                        else:
                            amount_total_tax = amount_untaxed + amount_tax
                            amount_untaxed_new = amount_total_tax / 1.07
                            amount_tax_new = amount_total_tax - amount_untaxed_new
                            order.update({
                                'amount_untaxed': amount_untaxed_new + amount_none_taxed,
                                'amount_tax': amount_tax_new,
                                'amount_total': amount_untaxed + amount_none_taxed + amount_tax - order_discount,
                                'discounted_amount': order_discount,
                            })
                else:
                    # order.update({
                    #         'amount_untaxed': amount_untaxed,
                    #         'amount_tax': amount_tax,
                    #         'amount_total': amount_untaxed + amount_tax ,
                    #         })
                    amount_total = amount_untaxed + amount_none_taxed + amount_tax
                    if not amount_none_taxed:
                        order.update({
                            'amount_untaxed': amount_total / 1.07,
                            'amount_tax': amount_total - amount_total / 1.07,
                            'amount_total': amount_total,
                        })
                    else:
                        amount_total_tax = amount_untaxed + amount_tax
                        amount_untaxed_new = amount_total_tax / 1.07
                        amount_tax_new = amount_total_tax - amount_untaxed_new
                        order.update({
                            'amount_untaxed': amount_untaxed_new + amount_none_taxed,
                            'amount_tax': amount_tax_new,
                            'amount_total': amount_untaxed + amount_none_taxed + amount_tax - order_discount,
                            'discounted_amount': order_discount,
                        })
            else:
                # order.update({
                #     'amount_untaxed': amount_untaxed,
                #     'amount_tax': amount_tax,
                #     'amount_total': amount_untaxed + amount_tax ,
                #     })
                amount_total = amount_untaxed + amount_none_taxed + amount_tax
                if not amount_none_taxed:
                    order.update({
                        'amount_untaxed': amount_total / 1.07,
                        'amount_tax': amount_total - amount_total / 1.07,
                        'amount_total': amount_total,
                    })
                else:
                    amount_total_tax = amount_untaxed + amount_tax
                    amount_untaxed_new = amount_total_tax / 1.07
                    amount_tax_new = amount_total_tax - amount_untaxed_new
                    order.update({
                        'amount_untaxed': amount_untaxed_new + amount_none_taxed,
                        'amount_tax': amount_tax_new,
                        'amount_total': amount_untaxed + amount_none_taxed + amount_tax - order_discount,
                        'discounted_amount': order_discount,
                    })

    def action_view_invoice(self):
        '''
        This function returns an action that display existing vendor bills of given purchase order ids.
        When only one found, show the vendor bill immediately.
        '''
        action = self.env.ref('account.action_move_in_invoice_type')
        result = action.read()[0]
        create_bill = self.env.context.get('create_bill', False)
        # override the context to get rid of the default filtering
        result['context'] = {
            'default_type': 'in_invoice',
            'default_company_id': self.company_id.id,
            'default_purchase_id': self.id,
            'default_discount_apply_type' : self.discount_apply_type ,
            'default_discounted_amount' : self.discounted_amount,
            'default_discount_value' : self.discount_value ,
            'default_discount_type' : self.discount_type,
            'default_discount_amt_line' : self.discount_amt_line,
            'default_amount_untaxed' : self.amount_untaxed,
            'default_type_id': self.type_id.id,
            'default_journal_id': self.type_id.journal_id.id,
            'default_narration': 'TEST',
        }
        # choose the view_mode accordingly
        if len(self.invoice_ids) > 1 and not create_bill:
            result['domain'] = "[('id', 'in', " + str(self.invoice_ids.ids) + ")]"
        else:
            res = self.env.ref('account.view_move_form', False)
            form_view = [(res and res.id or False, 'form')]
            if 'views' in result:
                result['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                result['views'] = form_view
            # Do not set an invoice_id if we want to create a new bill.
            if not create_bill:
                result['res_id'] = self.invoice_ids.id or False
        result['context']['default_invoice_origin'] = self.name
        result['context']['default_ref'] = self.partner_ref
        return result

    # discount_type = fields.Selection([('Fixed', 'Fixed'), ('Percentage', 'Percentage')], 'Discount Method')
    # discount_value = fields.Float('Discount Amount')
    # discounted_amount = fields.Monetary(compute='_amount_all', string='- Discount',
    #                                     digits_compute=dp.get_precision('Discount'), store=True, readonly=True)
    # discount_apply_type = fields.Selection([('line', 'Order Line'), ('global', 'Global')], string='Discount Applies to',
    #                                        default='global')
    # discount_amt_line = fields.Float(compute='_amount_all', string='- Line Discount',
    #                                  digits_compute=dp.get_precision('Line Discount'), store=True, readonly=True)

    tax_discount_policy = fields.Selection([('tax', 'Tax Amount'), ('untax', 'Untax Amount')],
                                           string='Discount Applies On', default='untax')
    discount_type = fields.Selection([('Fixed', 'Fixed'), ('Percentage', 'Percentage')], 'Discount Method',default='Fixed')
    discount_value = fields.Float('Discount Amount',default=0.0)
    discounted_amount = fields.Monetary(compute='_amount_all',store=True,string='- Discount',readonly=True)
    discount_apply_type = fields.Selection([('line', 'Order Line'), ('global', 'Global')],string='Discount Applies to',default='global')
    discount_amt_line = fields.Float(compute='_amount_all', string='- Line Discount', digits_compute=dp.get_precision('Line Discount'), store=True, readonly=True)


# class purchase_order_line(models.Model):
#     _inherit = 'purchase.order.line'
#
#     discount_type = fields.Selection(
#             [('Fixed', 'Fixed'), ('Percentage', 'Percentage')], 'Discount Method')
#     discount_apply_type = fields.Selection(related='order_id.discount_apply_type', string="Discount Applies to")
#     discount_amount = fields.Float('Discount Amount')
#     discount_amt = fields.Float('Discount Final Amount')
#
#     @api.depends('product_qty', 'price_unit', 'taxes_id','discount_apply_type','discount_amount','discount_type')
#     def _compute_amount(self):
#         for line in self:
#             vals = line._prepare_compute_all_values()
#             res_config= self.env['res.config.settings'].search([],order="id desc", limit=1)
#             if res_config:
#                 if res_config.tax_discount_policy == 'untax':
#                     if line.discount_apply_type == 'line':
#                         if line.discount_type == 'Fixed' and not line.taxes_id.price_include == True:
#                             price = (vals['price_unit'] * vals['product_qty']) - line.discount_amount
#                             taxes = line.taxes_id.compute_all(price,vals['currency_id'],1,vals['product'],vals['partner'])
#                             line.update({
#                                 'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
#                                 'price_total': taxes['total_included'] + line.discount_amount,
#                                 'price_subtotal': taxes['total_excluded'] + line.discount_amount,
#                                 'discount_amt' : line.discount_amount,
#                             })
#                         elif line.discount_type == 'Fixed' and  line.taxes_id.price_include == True:
#                             price = (vals['price_unit'] * vals['product_qty'])
#                             taxes = line.taxes_id.compute_all(price,vals['currency_id'],1,vals['product'],vals['partner'])
#                             line.update({
#                                 'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
#                                 'price_total': taxes['total_included'],
#                                 'price_subtotal': taxes['total_excluded'],
#                                 'discount_amt' : line.discount_amount,
#                             })
#                         elif line.discount_type == 'Percentage' and not line.taxes_id.price_include == True:
#                             price = (vals['price_unit'] * vals['product_qty']) * (1 - (line.discount_amount or 0.0) / 100.0)
#                             price_x = ((vals['price_unit'] * vals['product_qty'])-((vals['price_unit'] * vals['product_qty']) * (1 - (line.discount_amount or 0.0) / 100.0)))
#                             taxes = line.taxes_id.compute_all(price,vals['currency_id'],1,vals['product'],vals['partner'])
#                             line.update({
#                                 'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
#                                 'price_total': taxes['total_included'] + price_x,
#                                 'price_subtotal': taxes['total_excluded'] + price_x,
#                                 'discount_amt' : price_x,
#                             })
#                         elif line.discount_type == 'Percentage' and  line.taxes_id.price_include == True:
#                             price = vals['price_unit']
#                             taxes = line.taxes_id.compute_all(price,vals['currency_id'],1,vals['product'],vals['partner'])
#                             price_x = ((taxes['total_excluded'] * vals['product_qty'])-((taxes['total_excluded'] * vals['product_qty']) * (1 - (line.discount_amount or 0.0) / 100.0)))
#
#                             line.update({
#                                 'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
#                                 'price_total': taxes['total_included'],
#                                 'price_subtotal': taxes['total_excluded'],
#                                 'discount_amt' : price_x,
#                             })
#                         else:
#                             taxes = line.taxes_id.compute_all(vals['price_unit'],vals['currency_id'],vals['product_qty'],vals['product'],vals['partner'])
#                             line.update({
#                                 'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
#                                 'price_total': taxes['total_included'],
#                                 'price_subtotal': taxes['total_excluded'],
#                             })
#                     else:
#                         taxes = line.taxes_id.compute_all(vals['price_unit'],vals['currency_id'],vals['product_qty'],vals['product'],vals['partner'])
#                         line.update({
#                             'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
#                             'price_total': taxes['total_included'],
#                             'price_subtotal': taxes['total_excluded'],
#                         })
#                 elif res_config.tax_discount_policy == 'tax':
#                     price_x = 0.0
#                     if line.discount_apply_type == 'line':
#                         taxes = line.taxes_id.compute_all(vals['price_unit'],vals['currency_id'],vals['product_qty'],vals['product'],vals['partner'])
#                         if line.discount_type == 'Fixed':
#                             price_x = (taxes['total_included']) - (taxes['total_included'] - line.discount_amount)
#                         elif line.discount_type == 'Percentage':
#                             price_x = (taxes['total_included']) - (taxes['total_included'] * (1 - (line.discount_amount or 0.0) / 100.0))
#
#                         line.update({
#                             'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
#                             'price_total': taxes['total_included'],
#                             'price_subtotal': taxes['total_excluded'],
#                             'discount_amt' : price_x,
#                         })
#                     else:
#                         taxes = line.taxes_id.compute_all(vals['price_unit'],vals['currency_id'],vals['product_qty'],vals['product'],vals['partner'])
#                         line.update({
#                             'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
#                             'price_total': taxes['total_included'],
#                             'price_subtotal': taxes['total_excluded'],
#                         })
#                 else:
#                     taxes = line.taxes_id.compute_all(vals['price_unit'],vals['currency_id'],vals['product_qty'],vals['product'],vals['partner'])
#                     line.update({
#                         'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
#                         'price_total': taxes['total_included'],
#                         'price_subtotal': taxes['total_excluded'],
#                     })
#             else:
#                 taxes = line.taxes_id.compute_all(vals['price_unit'],vals['currency_id'],vals['product_qty'],vals['product'],vals['partner'])
#                 line.update({
#                     'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
#                     'price_total': taxes['total_included'],
#                     'price_subtotal': taxes['total_excluded'],
#                 })
#
#     def _prepare_account_move_line(self, move):
#         res =super(purchase_order_line,self)._prepare_account_move_line(move)
#         # res.update({'discount_apply_type':self.discount_apply_type,'discount_amount':self.discount_amount,})
#         return res
