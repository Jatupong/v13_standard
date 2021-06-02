# -*- coding: utf-8 -*-
from __future__ import division
from odoo import api, fields, models, _
# import openerp.addons.decimal_precision as dp
import odoo.addons.decimal_precision as dp



class purchaseorder_discount(models.Model):
    _inherit = 'purchase.order'

    discount_view = fields.Selection([('After Tax', 'After Tax'), ('Before Tax', 'Before Tax')], default='Before Tax',string='Discount Type',
                                     states={'draft': [('readonly', False)]},
                                     help='Choose If After or Before applying Taxes type of the Discount')
    discount_type = fields.Selection([('Fixed', 'Fixed'), ('Percentage', 'Percentage')], string='Discount Method',
                                     states={'draft': [('readonly', False)]})
    discount_value = fields.Float(string='Discount Value', states={'draft': [('readonly', False)]},
                                  help='Choose the value of the Discount')
    discounted_amount = fields.Float(compute='disc_amount', string='Discounted Amount', readonly=True)

    amount_total = fields.Float(string='Total', digits=dp.get_precision('Account'),
                                store=True, readonly=True, compute='_amount_all')


    @api.depends('order_line.price_total','discount_type', 'discount_value')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        s_id = self.env['account.tax'].search([('tax_report','=',True),('type_tax_use','=','purchase')],limit=1)

        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax

            #add for discount calculation
            if self.discount_view == 'After Tax':
                if self.discount_type == 'Fixed':
                    amount_total = amount_untaxed + amount_tax - self.discount_value
                elif self.discount_type == 'Percentage':
                    amount_to_dis = (amount_untaxed + amount_tax) * (self.discount_value / 100)
                    amount_total = (amount_untaxed + amount_tax) - amount_to_dis
                else:
                    amount_total = amount_untaxed + amount_tax
            elif self.discount_view == 'Before Tax':
                if self.discount_type == 'Fixed':
                    the_value_before = amount_untaxed - self.discount_value
                    if s_id.amount:
                        the_tax_before = amount_tax - (self.discount_value * s_id.amount / 100)
                    else:
                        the_tax_before = amount_tax - (self.discount_value * 0.07)
                    amount_tax = the_tax_before
                    amount_total = the_value_before + the_tax_before
                elif self.discount_type == 'Percentage':
                    amount_to_dis = round(amount_untaxed * (self.discount_value / 100),2)
                    the_value_before = amount_untaxed - amount_to_dis
                    if s_id.amount:
                        the_tax_before = amount_tax - (amount_to_dis * s_id.amount / 100)
                    else:
                        the_tax_before = amount_tax - (amount_to_dis * 0.07)

                    amount_tax = round(the_tax_before,2)
                    amount_total = the_value_before + round(the_tax_before,2)
                else:
                    amount_total = amount_untaxed + amount_tax
            else:
                amount_total = amount_untaxed + amount_tax


            order.update({
                'amount_untaxed': order.currency_id.round(amount_untaxed),
                'amount_tax': order.currency_id.round(amount_tax),
                'amount_total': amount_total,
            })


    @api.depends('order_line.price_subtotal', 'discount_type', 'discount_value')
    def disc_amount(self):

        if self.discount_view == 'After Tax':
            if self.discount_type == 'Fixed':
                self.discounted_amount = self.discount_value
            elif self.discount_type == 'Percentage':
                amount_to_dis = (self.amount_untaxed + self.amount_tax) * (self.discount_value / 100)
                self.discounted_amount = amount_to_dis
            else:
                self.discounted_amount = 0
        elif self.discount_view == 'Before Tax':
            if self.discount_type == 'Fixed':
                self.discounted_amount = self.discount_value
            elif self.discount_type == 'Percentage':
                amount_to_dis = self.amount_untaxed * (self.discount_value / 100)
                self.discounted_amount = round(amount_to_dis,2)
            else:
                self.discounted_amount = 0
        else:
            self.discounted_amount = 0
