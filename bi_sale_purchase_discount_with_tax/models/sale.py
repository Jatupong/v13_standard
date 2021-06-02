# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import odoo.addons.decimal_precision as dp
from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from odoo.tools import float_is_zero, float_compare


class sale_order(models.Model):
    _inherit = 'sale.order'


    @api.depends('discount_value','discount_apply_type','discount_type')
    def _calculate_discount(self):
        res=0.0
        discount = 0.0
        for self_obj in self:
            if self_obj.discount_type == 'Fixed':
                discount = self_obj.discount_value
                res = discount
            elif self_obj.discount_type == 'Percentage':
                if self_obj.order_line and self_obj.order_line[0].tax_id and self_obj.order_line[0].tax_id[
                    0].price_include:
                    discount = (self_obj.amount_untaxed + self_obj.amount_tax) * (self_obj.discount_value/ 100)
                else:
                    discount = self_obj.amount_untaxed * (self_obj.discount_value / 100)
                res = discount
            else:
                res = discount

        print ('CAL DISCOUNT')
        print (res)
        return res

    def update_discount_button(self):
        for order in self.env['sale.order'].search([]):
            print (order.name)
            order._amount_all()

        for order in self.env['purchase.order'].search([]):
            print(order.name)
            order._amount_all()


    @api.depends('order_line','order_line.price_total','order_line.price_subtotal',\
        'order_line.product_uom_qty','discount_value',\
        'discount_apply_type','discount_type')
    # @api.depends('order_line', 'order_line.price_total', 'order_line.price_subtotal', \
    #              'order_line.product_uom_qty', 'discount_value', \
    #              'discount_apply_type', 'discount_type', 'order_line.discount_amount', \
    #              'order_line.discount_type', 'order_line.discount_amt')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        res_config= self.env['res.config.settings'].sudo().search([],order="id desc", limit=1)
        cur_obj = self.env['res.currency']
        for order in self:                      
            applied_discount = line_discount = sums = order_discount =  amount_untaxed = amount_none_taxed = amount_tax = amount_after_discount =  order_discount_tax = 0.0

            for line in order.order_line:
                # print ('--LINE SUB TOTAL TAX')
                # print (line.price_subtotal)
                # print (line.price_tax)
                if line.tax_id:
                    amount_untaxed += line.price_subtotal
                else:
                    amount_none_taxed += line.price_subtotal

                amount_tax += line.price_tax
                print ('-AMOUN TAX')
                print (amount_tax)
                # applied_discount += line.discount_amt

            # print (amount_untaxed)
            # print (amount_tax)
                # remove#1 - JA - 01/02/2021
                # if line.discount_type == 'Fixed':
                #     line_discount += line.discount_amount
                # elif line.discount_type == 'Percentage':
                #     #line_discount += line.price_unit * (line.discount_amount/ 100)
                #     line_discount += line.price_subtotal * (line.discount_amount/ 100)


            # print ('---RES CONFIG')
            # print (res_config)
            # print (res_config.tax_discount_policy)
            # print(res_config.quotation_validity_days)
            # print(res_config.purchase_account_id)
            # print ('---END CONFIG--')
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
                            order_discount = amount_untaxed * (order.discount_value / 100)
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
                        #     if line.discount_type == 'Fixed' and line.tax_id.price_include == True:
                        #         price_amount = amount_untaxed - line.discount_amount
                        #         taxes = line.tax_id.compute_all(price_amount, line.order_id.currency_id, 1, product=line.product_id, partner=line.order_id.partner_shipping_id)
                        #         sums += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
                        #     elif line.discount_type == 'Percentage' and line.tax_id.price_include == True:
                        #         price_amount = line.price_subtotal - ((line.discount_amount*line.price_subtotal)/100.0)
                        #         taxes = line.tax_id.compute_all(price_amount, line.order_id.currency_id, 1, product=line.product_id, partner=line.order_id.partner_shipping_id)
                        #         sums += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
                        #     elif line.discount_type == 'Fixed' and not line.tax_id.price_include == True:
                        #         sums = amount_tax
                        #     elif line.discount_type == 'Percentage' and not line.tax_id.price_include == True:
                        #         sums = amount_tax
                        #     else:
                        #         sums = amount_tax
                        # order.update({
                        #     'amount_untaxed': amount_untaxed,
                        #     'amount_tax': sums,
                        #     'amount_total': amount_untaxed + sums - applied_discount,
                        #     'discount_amt_line' : applied_discount,
                        # })
                    elif order.discount_apply_type == 'global':
                        order.discount_amt_line = 0.00
                        order_line_taxes_ids = order.order_line.filtered(lambda x: x.tax_id)
                        
                        if order.discount_type == 'Percentage':

                            if order_line_taxes_ids and order_line_taxes_ids[0].tax_id and order_line_taxes_ids[0].tax_id[
                                0].price_include:
                                order_discount = (amount_untaxed + amount_none_taxed + amount_tax) * (order.discount_value / 100)
                            else:
                                order_discount = (amount_untaxed + amount_none_taxed) * (order.discount_value / 100)

                            if order_line_taxes_ids and order_line_taxes_ids[0].tax_id and order_line_taxes_ids[0].tax_id[
                                0].price_include and \
                                    order_line_taxes_ids[0].tax_id[0].amount:
                                order_discount_tax = order_discount - order_discount/((100 + order.order_line[0].tax_id[0].amount) * 0.01)
                                order_discount_untaxed = order_discount/((100 + order.order_line[0].tax_id[0].amount) * 0.01)

                            elif order_line_taxes_ids and order_line_taxes_ids[0].tax_id and not order_line_taxes_ids[0].tax_id[
                                    0].price_include and \
                                        order_line_taxes_ids[0].tax_id[0].amount:
                                order_discount_tax = order_discount*(order_line_taxes_ids[0].tax_id[0].amount) * 0.01
                                order_discount_untaxed = order_discount
                            else:
                                order_discount_untaxed = order_discount

                            #option-1
                            # order.update({
                            #     'amount_untaxed': amount_untaxed - order_discount_untaxed,
                            #     'amount_tax': amount_tax - order_discount_tax,
                            #     'amount_total': amount_untaxed + amount_tax - order_discount_tax - order_discount_untaxed,
                            #     'discounted_amount': order_discount,
                            # })
                            #option-2
                            amount_total = amount_untaxed + amount_none_taxed + amount_tax - order_discount_tax - order_discount_untaxed
                            if not amount_none_taxed and amount_tax:
                                order.update({
                                    'amount_total': amount_untaxed + amount_tax - order_discount_tax - order_discount_untaxed,
                                    'amount_untaxed': amount_total / 1.07,
                                    'amount_tax': amount_total - amount_total / 1.07,
                                    'discounted_amount': order_discount,
                                })
                            elif amount_none_taxed and amount_tax:
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
                                amount_total_tax = amount_untaxed + amount_none_taxed + amount_tax - order_discount
                                # amount_untaxed_new = amount_total_tax / 1.07
                                # amount_tax_new = amount_total_tax - amount_untaxed_new
                                order.update({
                                    'amount_untaxed': amount_total_tax,
                                    'amount_tax': amount_tax,
                                    'amount_total': amount_total_tax,
                                    'discounted_amount': order_discount,
                                })

                        elif order.discount_type == 'Fixed':
                            order_discount = order.discount_value

                            if order_line_taxes_ids and order_line_taxes_ids[0].tax_id and order_line_taxes_ids[0].tax_id[
                                0].price_include and \
                                    order_line_taxes_ids[0].tax_id[0].amount:
                                order_discount_tax = order_discount - order_discount/((100 + order_line_taxes_ids[0].tax_id[0].amount) * 0.01)
                                order_discount_untaxed = order_discount/((100 + order_line_taxes_ids[0].tax_id[0].amount) * 0.01)
                            elif order_line_taxes_ids and order_line_taxes_ids[0].tax_id and not order_line_taxes_ids[0].tax_id[
                                    0].price_include and \
                                        order_line_taxes_ids[0].tax_id[0].amount:
                                order_discount_tax = order_discount*((order_line_taxes_ids[0].tax_id[0].amount) * 0.01)
                                order_discount_untaxed = order_discount
                            else:
                                order_discount_untaxed = order_discount

                            # print ('DIS Update--')
                            # print (amount_untaxed)
                            # print (amount_tax)
                            # print (order_discount_tax)
                            # print (order_discount_untaxed)

                            #option-1
                            # order.update({
                            #     'amount_untaxed': amount_untaxed - order_discount_untaxed,
                            #     'amount_tax': amount_tax - order_discount_tax,
                            #     'amount_total': amount_untaxed + amount_tax - order_discount_tax - order_discount_untaxed,
                            #     'discounted_amount': order_discount,
                            # })
                            # option-2
                            # amount_total = amount_untaxed + amount_tax - order_discount_tax - order_discount_untaxed
                            amount_total = amount_untaxed + amount_none_taxed + amount_tax - order_discount_tax - order_discount_untaxed
                            if not amount_none_taxed and amount_tax:
                                order.update({
                                    'amount_total': amount_untaxed + amount_tax - order_discount_tax - order_discount_untaxed,
                                    'amount_untaxed': amount_total / 1.07,
                                    'amount_tax': amount_total - amount_total / 1.07,
                                    'discounted_amount': order_discount,
                                })
                            elif amount_none_taxed and amount_tax:
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
                            # super(sale_order,)

                            amount_total = amount_untaxed + amount_none_taxed + amount_tax
                            # order.update({
                            #     'amount_untaxed': amount_untaxed,
                            #     'amount_tax': amount_tax,
                            #     'amount_total': amount_untaxed + amount_tax - order_discount,
                            #     'discounted_amount': order_discount,
                            # })
                            if not amount_none_taxed and amount_tax:
                                order.update({
                                    'amount_untaxed': amount_total/1.07,
                                    'amount_tax': amount_total - amount_total/1.07,
                                    'amount_total': amount_total ,
                                })
                            elif amount_none_taxed and amount_tax:
                                amount_total_tax = amount_untaxed + amount_tax
                                amount_untaxed_new = amount_total_tax/1.07
                                amount_tax_new = amount_total_tax - amount_untaxed_new
                                order.update({
                                    'amount_untaxed': amount_untaxed_new + amount_none_taxed,
                                    'amount_tax': amount_tax_new,
                                    'amount_total': amount_untaxed + amount_none_taxed + amount_tax - order_discount,
                                    'discounted_amount': order_discount,
                                })
                            else:
                                super(sale_order, self)._amount_all()

                    else:
                        amount_total = amount_untaxed + amount_none_taxed + amount_tax
                        # order.update({
                        #     'amount_untaxed': amount_untaxed,
                        #     'amount_tax': amount_tax,
                        #     'amount_total': amount_untaxed + amount_tax - order_discount,
                        #     'discounted_amount': order_discount,
                        # })
                        if not amount_none_taxed and amount_tax:
                            order.update({
                                'amount_untaxed': amount_total / 1.07,
                                'amount_tax': amount_total - amount_total / 1.07,
                                'amount_total': amount_total,
                            })
                        elif amount_none_taxed and amount_tax:
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
                            super(sale_order, self)._amount_all()
                else:
                    amount_total = amount_untaxed + amount_none_taxed + amount_tax
                    # order.update({
                    #     'amount_untaxed': amount_untaxed,
                    #     'amount_tax': amount_tax,
                    #     'amount_total': amount_untaxed + amount_tax - order_discount,
                    #     'discounted_amount': order_discount,
                    # })
                    if not amount_none_taxed and amount_tax:
                        order.update({
                            'amount_untaxed': amount_total / 1.07,
                            'amount_tax': amount_total - amount_total / 1.07,
                            'amount_total': amount_total,
                        })
                    elif amount_none_taxed and amount_tax:
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
                        super(sale_order, self)._amount_all()

            else:
                amount_total = amount_untaxed + amount_none_taxed + amount_tax
                # order.update({
                #     'amount_untaxed': amount_untaxed,
                #     'amount_tax': amount_tax,
                #     'amount_total': amount_untaxed + amount_tax - order_discount,
                #     'discounted_amount': order_discount,
                # })
                #if no someitem without vat
                if not amount_none_taxed and amount_tax:
                    order.update({
                        'amount_untaxed': amount_total / 1.07,
                        'amount_tax': amount_total - amount_total / 1.07,
                        'amount_total': amount_total,
                    })
                elif amount_none_taxed and amount_tax:
                    #if some item is none vat
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
                    super(sale_order, self)._amount_all()

    tax_discount_policy = fields.Selection([('tax', 'Tax Amount'), ('untax', 'Untax Amount')],string='Discount Applies On',default='untax')
    discount_type = fields.Selection([('Fixed', 'Fixed'), ('Percentage', 'Percentage')], 'Discount Method')
    discount_value = fields.Float('Discount Amount')
    discounted_amount = fields.Monetary(compute='_amount_all', string='- Discount', digits_compute=dp.get_precision('Discount'), store=True, readonly=True)
    discount_apply_type = fields.Selection([('line', 'Order Line'), ('global', 'Global')],string='Discount Applies to',default='global')
    discount_amt_line = fields.Float(compute='_amount_all', string='- Line Discount', digits_compute=dp.get_precision('Line Discount'), store=True, readonly=True)

    def _prepare_invoice(self):
        res = super(sale_order,self)._prepare_invoice()
        res.update({'discount_type': self.discount_type,
                'discount_value': self.discount_value,
                'discounted_amount': self.discounted_amount,
                'discount_apply_type': self.discount_apply_type,
                'discount_amt_line' : self.discount_amt_line,
                'is_line' : True,})
        return res



class res_company(models.Model):
    _inherit = 'res.company'

    tax_discount_policy = fields.Selection([('tax', 'Tax Amount'), ('untax', 'Untax Amount')],
                                           string='Discount Applies On', default='tax',
                                           default_model='sale.order')
    sale_account_id = fields.Many2one('account.account', 'Sale Discount Account',
                                      domain=[('user_type_id.name', '=', 'Expenses'), ('discount_account', '=', True)])
    purchase_account_id = fields.Many2one('account.account', 'Purchase Discount Account',
                                          domain=[('user_type_id.name', '=', 'Income'),
                                                  ('discount_account', '=', True)])


# class ResConfigSettings(models.TransientModel):
#     _inherit = 'res.config.settings'
#
#     tax_discount_policy = fields.Selection([('tax', 'Tax Amount'), ('untax', 'Untax Amount')],string='Discount Applies On',default='tax',
#         default_model='sale.order')
#     sale_account_id = fields.Many2one('account.account', 'Sale Discount Account',domain=[('user_type_id.name','=','Expenses'), ('discount_account','=',True)])
#     purchase_account_id = fields.Many2one('account.account', 'Purchase Discount Account',domain=[('user_type_id.name','=','Income'), ('discount_account','=',True)])
#
#     @api.model
#     def get_values(self):
#         res = super(ResConfigSettings, self).get_values()
#         ICPSudo = self.env['ir.config_parameter'].sudo()
#         tax_discount_policy = ICPSudo.get_param('bi_sale_purchase_discount_with_tax.tax_discount_policy')
#         sale_account_id = ICPSudo.get_param('bi_sale_purchase_discount_with_tax.sale_account_id')
#         purchase_account_id = ICPSudo.get_param('bi_sale_purchase_discount_with_tax.purchase_account_id')
#         res.update(tax_discount_policy=tax_discount_policy,sale_account_id=int(sale_account_id),purchase_account_id=int(purchase_account_id),)
#         return res
#
#     def set_values(self):
#
#         super(ResConfigSettings, self).set_values()
#         for rec in self:
#             ICPSudo = rec.env['ir.config_parameter'].sudo()
#             ICPSudo.set_param('bi_sale_purchase_discount_with_tax.sale_account_id',rec.sale_account_id.id)
#             ICPSudo.set_param('bi_sale_purchase_discount_with_tax.purchase_account_id',rec.purchase_account_id.id)
#             ICPSudo.set_param('bi_sale_purchase_discount_with_tax.tax_discount_policy',str(rec.tax_discount_policy))
