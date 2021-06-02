# -*- coding: utf-8 -*-
from __future__ import division
from odoo import fields, models, api

class saleorder_discount(models.Model):
    _inherit = 'sale.order'

    discount_view = fields.Selection([('After Tax', 'After Tax'), ('Before Tax', 'Before Tax')], string='Discount Type',
                                     states={'draft': [('readonly', False)]},
                                     help='Choose If After or Before applying Taxes type of the Discount')
    discount_type = fields.Selection([('Fixed', 'Fixed'), ('Percentage', 'Percentage')], string='Discount Method',
                                     states={'draft': [('readonly', False)]})
    discount_value = fields.Float(string='Discount Value', states={'draft': [('readonly', False)]},
                                  help='Choose the value of the Discount')
    discounted_amount = fields.Float(compute='disc_amount', string='Discounted Amount', readonly=True)

    def _prepare_invoice(self):
        res = super(saleorder_discount, self)._prepare_invoice()
        if self.discount_view:
            res.update({'discount_view':self.discount_view,
                        'discount_type': self.discount_type,
                        'discount_value': self.discount_value,
                        'discounted_amount': self.discounted_amount
                        })
        return res

    @api.depends('order_line.price_total', 'discount_type', 'discount_value')
    def _amount_all(self):
        for order in self:
            taxes_id = sum(order.order_line.mapped('tax_id').mapped('amount'))
            amount_untaxed = amount_tax = 0.0

            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                if order.company_id.tax_calculation_rounding_method == 'round_globally':
                    price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                    taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=order.partner_shipping_id)
                    amount_tax += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))

                else:
                    amount_tax += line.price_tax

            #add for discount calculation
            if order.discount_view == 'After Tax':
                if order.discount_type == 'Fixed':
                    amount_total = amount_untaxed + amount_tax - order.discount_value
                else:
                    amount_to_dis = (amount_untaxed + amount_tax) * (order.discount_value * 0.01)
                    amount_total = (amount_untaxed + amount_tax) - amount_to_dis

            elif order.discount_view == 'Before Tax':
                if order.discount_type == 'Fixed':
                    the_value_before = amount_untaxed - order.discount_value
                    amount_tax = amount_tax - (order.discount_value * taxes_id * 0.01)
                else:
                    amount_to_dis = amount_untaxed * (order.discount_value * 0.01)
                    the_value_before = amount_untaxed - amount_to_dis
                    amount_tax = amount_tax - (amount_to_dis * taxes_id * 0.01)
                amount_total = the_value_before + amount_tax

            else:
                amount_total = amount_untaxed + amount_tax

            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
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
                # 'discounted_amount': order.currency_id.round(discounted_amount),
                'discounted_amount': round(discounted_amount, 2)
            })

# saleorder_discount()

# class SaleOrderLine(models.Model):
#     _inherit = "sale.order.line"
#
#
#     discount_amount = fields.Float('Discount (Amount)', default=0.0)
#
#
#     #option discount amount per unit or price sub total
#     @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id', 'discount_amount')
#     def _compute_amount(self):
#         """
#         Compute the amounts of the SO line.
#         """
#         for line in self:
#             price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
#             if line.discount_amount > 0.0:
#                 if self.env.user.company_id.discount_amount_condition and self.env.user.company_id.discount_amount_condition == 'unit':
#                     price -= line.discount_amount
#                 else:
#                     price -= line.discount_amount/line.product_uom_qty
#
#             taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
#                                             product=line.product_id, partner=line.order_id.partner_id)
#             line.update({
#                 'price_tax': taxes['total_included'] - taxes['total_excluded'],
#                 'price_total': taxes['total_included'],
#                 'price_subtotal': taxes['total_excluded'],
#             })



class res_company(models.Model):
    _inherit = "res.company"

    # sale_condition = fields.Text(string="เงื่อนไขการรับประกันสินค้า",translate=True)
    discount_amount_condition = fields.Selection([
        ('unit','Per Unit'),
        ('total','Per Total')
    ],default='total',string="Discount Amount Condition")
