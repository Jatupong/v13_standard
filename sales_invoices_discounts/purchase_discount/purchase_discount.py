# -*- coding: utf-8 -*-
from __future__ import division
from odoo import api, fields, models, _


class purchaseorder_discount(models.Model):
    _inherit = 'purchase.order'

    discount_view = fields.Selection([('After Tax', 'After Tax'),('Before Tax', 'Before Tax')], string='Discount Type',
                                     states={'draft': [('readonly', False)]},
                                     help='Choose If After or Before applying Taxes type of the Discount')
    discount_type = fields.Selection([('Fixed', 'Fixed'), ('Percentage', 'Percentage')], string='Discount Method',
                                     states={'draft': [('readonly', False)]})
    discount_value = fields.Float(string='Discount Value', states={'draft': [('readonly', False)]},
                                  help='Choose the value of the Discount')
    discounted_amount = fields.Float(compute='disc_amount', string='Discounted Amount', readonly=True)

    @api.depends('order_line.price_total','discount_type', 'discount_value')
    def _amount_all(self):
        for order in self:
            taxes = sum(order.order_line.mapped('taxes_id').mapped('amount'))
            # print('taxes amount :',taxes)
            amount_untaxed = amount_tax = 0.0
            super(purchaseorder_discount, self)._amount_all()

            if order.discount_view:
                # print('discount_view :',order.discount_view)
                for line in order.order_line:
                    amount_untaxed += line.price_subtotal
                    amount_tax += line.price_tax

                if order.discount_view == 'After Tax':
                    if order.discount_type == 'Fixed':
                        amount_total = amount_untaxed + amount_tax - order.discount_value
                    else:
                        amount_to_dis = (amount_untaxed + amount_tax) * (order.discount_value * 0.01)
                        amount_total = (amount_untaxed + amount_tax) - amount_to_dis

                elif order.discount_view == 'Before Tax':
                    if order.discount_type == 'Fixed':
                        the_value_before = amount_untaxed - order.discount_value
                        amount_tax = amount_tax - (order.discount_value * taxes * 0.01)
                    else:
                        amount_to_dis = amount_untaxed * (order.discount_value * 0.01)
                        the_value_before = amount_untaxed - amount_to_dis
                        amount_tax = amount_tax - (amount_to_dis * taxes * 0.01)
                    amount_total = the_value_before + amount_tax

                else:
                    amount_total = amount_untaxed + amount_tax

                # print('amount_tax : ', amount_tax)
                # print('amount_total : ', amount_total)
                order.update({
                    'amount_tax': order.currency_id.round(amount_tax),
                    'amount_total': amount_total,
                })

    @api.depends('order_line.price_subtotal', 'discount_type', 'discount_value')
    def disc_amount(self):
        for order in self:
            discounted_amount = 0.0
            if order.discount_view:
                if order.discount_view == 'After Tax':
                    amount_tax = order.amount_tax
                elif order.discount_view == 'Before Tax':
                    amount_tax = 0.0

                if order.discount_type == 'Fixed':
                    discounted_amount = order.discount_value
                else:
                    discounted_amount = (order.amount_untaxed + amount_tax) * (order.discount_value * 0.01)

            order.update({
                'discounted_amount': order.currency_id.round(discounted_amount),
            })

    def action_view_invoice(self):
        '''
        This function returns an action that display existing vendor bills of given purchase order ids.
        When only one found, show the vendor bill immediately.
        '''
        result = super(purchaseorder_discount, self).action_view_invoice()
        if self.discount_view:
            result['context'].update({
                'default_discount_view': self.discount_view,
                'default_discount_type': self.discount_type,
                'default_discount_value': self.discount_value,
                'default_discounted_amount': self.discounted_amount,
            })

        return result