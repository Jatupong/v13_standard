# -*- coding: utf-8 -*-
from __future__ import division
from odoo import fields, models, api
import odoo.addons.decimal_precision as dp


class saleorder_discount(models.Model):
    _inherit = 'sale.order'
    discount_view = fields.Selection([('After Tax', 'After Tax'), ('Before Tax', 'Before Tax')], default='Before Tax', string='Discount Type',
                                     states={'draft': [('readonly', False)]},
                                     help='Choose If After or Before applying Taxes type of the Discount')
    discount_type = fields.Selection([('Fixed', 'Fixed'), ('Percentage', 'Percentage')], string='Discount Method',
                                     states={'draft': [('readonly', False)]})
    discount_value = fields.Float(string='Discount Value', states={'draft': [('readonly', False)]},
                                  help='Choose the value of the Discount')
    discounted_amount = fields.Float(compute='disc_amount', string='Discounted Amount', readonly=True)


    amount_total = fields.Float(string='Total', digits=dp.get_precision('Account'),
                                store=True, readonly=True, compute='_amount_all')



    # def _prepare_invoice(self):
    #     res = super(saleorder_discount, self)._prepare_invoice()
    #     if self.discount_view and self.discount_type and self.discount_value:
    #         res['discount_view'] = self.discount_view
    #         res['discount_type'] = self.discount_type
    #         res['discount_value'] = self.discount_value
    #
    #     return res

    @api.depends('order_line.price_total','discount_type', 'discount_value')
    def _amount_all(self):
        for order in self:
            t_id = self.env['account.tax'].search([('tax_report','=',True),('type_tax_use','=','sale')],limit=1)
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                # amount_tax += line.price_tax

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
                elif order.discount_type == 'Percentage':
                    amount_to_dis = (amount_untaxed + amount_tax) * (order.discount_value / 100)
                    amount_total = (amount_untaxed + amount_tax) - amount_to_dis
                else:
                    amount_total = amount_untaxed + amount_tax
            elif order.discount_view == 'Before Tax':
                if order.discount_type == 'Fixed':
                    the_value_before = amount_untaxed - order.discount_value
                    if t_id.amount:
                        the_tax_before = amount_tax - (order.discount_value * t_id.amount / 100)
                    else:
                        the_tax_before = amount_tax - (order.discount_value * 0.07)
                    amount_tax = the_tax_before
                    amount_total = the_value_before + the_tax_before
                elif order.discount_type == 'Percentage':
                    amount_to_dis = round(amount_untaxed * (order.discount_value / 100),2)
                    the_value_before = amount_untaxed - amount_to_dis
                    if t_id.amount:
                        the_tax_before = amount_tax - (amount_to_dis * t_id.amount / 100)
                    else:
                        the_tax_before = amount_tax - (amount_to_dis * 0.07)

                    amount_tax = round(the_tax_before,2)
                    amount_total = the_value_before + round(the_tax_before,2)
                else:
                    amount_total = amount_untaxed + amount_tax
            else:
                amount_total = amount_untaxed + amount_tax


            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_total,
            })


    @api.depends('order_line.price_subtotal', 'discount_type', 'discount_value')
    def disc_amount(self):
        if self.discount_view == 'After Tax':
            if self.discount_type == 'Fixed':
                self.discounted_amount = self.discount_value
            elif self.discount_type == 'Percentage':
                amount_to_dis = (self.amount_untaxed + self.amount_tax) * (self.discount_value / 100)
                self.discounted_amount = round(amount_to_dis,2)
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
