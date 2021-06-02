from __future__ import division
from odoo import fields, models, api, _
import odoo.addons.decimal_precision as dp
# from odoo.tools import amount_to_text_en
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare
from odoo.tools.misc import formatLang, format_date, get_lang


class ResCompany(models.Model):
    _inherit = "res.company"

    default_sales_discount_account_id = fields.Many2one('account.account', string='Default Sales Discount Account')
    default_purchase_discount_account_id = fields.Many2one('account.account',
                                                           string='Default Purchase Discount Account')



class invoice_discount(models.Model):
    _inherit = 'account.move'

    discount_view = fields.Selection([('After Tax', 'After Tax'), ('Before Tax', 'Before Tax')], default='Before Tax', string='Discount Type',
                                     states={'draft': [('readonly', False)]},
                                     help='Choose If After or Before applying Taxes type of the Discount')

    discount_type = fields.Selection([('Fixed', 'Fixed'), ('Percentage', 'Percentage')], string='Discount Method',
                                     states={'draft': [('readonly', False)]},
                                     help='Choose the type of the Discount')
    discount_value = fields.Float(string='Discount Value', states={'draft': [('readonly', False)]},
                                  help='Choose the value of the Discount')
    discounted_amount = fields.Float(compute='disc_amount', string='Discounted Amount', readonly=True)
    amount_total = fields.Float(string='Total', digits=dp.get_precision('Account'),
                                store=True, readonly=True, compute='_compute_amount')



    @api.onchange('purchase_id')
    def purchase_order_change(self):
        print('----------NEW ONE----purchase_order_change----')
        if not self.purchase_id:
            return {}
        if not self.partner_id:
            self.partner_id = self.purchase_id.partner_id.id
        # if not self.discount_view:
        # if self.purchase_id.discount_view and self.purchase_id.discount_type and self.purchase_id.discount_value:
        print ('----------NEW ONE----purchase_order_change----')
        self.discount_view = self.purchase_id.discount_view
        self.discount_type = self.purchase_id.discount_type
        self.discount_value = self.purchase_id.discount_value

        return super(invoice_discount, self).purchase_order_change()


    def _compute_amount_after_discount(self):
        for self_obj in self:
            res = self.amount_untaxed - self_obj.discounted_amount
            return res

    @api.depends('amount_untaxed','discount_type', 'discount_value')
    def disc_amount(self):

        print ('---DISC AMOUNT---')

        if self.discount_view == 'Before Tax':
            # print('---BT-1')
            if self.discount_type == 'Fixed':
                # print('---BT-2')
                self.discounted_amount = self.discount_value
            elif self.discount_type == 'Percentage':
                # print('---BT-3')
                amount_to_dis = self.amount_untaxed * (self.discount_value / 100)
                self.discounted_amount = round(amount_to_dis,2)
            else:
                # print('---BT-4')
                self.discounted_amount = 0


        else:
            self.discounted_amount = 0


        ###################################
        if self._context.get('default_type') in ['out_invoice'] and self.discounted_amount:
            discount_vals = {
                'account_id': self.env.user.company_id.default_sales_discount_account_id.id,  ##self.out_discount_account.id,
                'debit': self.discounted_amount,
                'price_unit': - self.discounted_amount,
                'credit': 0.00,
                'quantity': 1,
                'name': 'Discount',
                'tax_ids':[(6, 0, [2])],
                'tag_ids': [(6, 0, [10])],
                'exclude_from_invoice_tab': True,
                # 'predict_override_default_account': True,
            }
            print('-DISCOUNT VAL')
            print(discount_vals)

            exist = False
            for line in self.line_ids:
                if line.account_id == self.env.user.company_id.default_sales_discount_account_id:
                    exist = True
                    line.update({'debit': self.discounted_amount})
                    line.update({'price_unit': -self.discounted_amount})
                    line._onchange_debit()
                    print('---EXIST---')
            if not exist:
                print ('---NEW---')
                discount_lines = self.line_ids.with_context(check_move_validity=False).new(discount_vals)
                # discount_lines = self.line_ids.new(discount_vals)

                self.line_ids += discount_lines
                discount_lines._onchange_debit()
                # discount_lines._onchange_debit()

            ###########Update #########################
            self.line_ids._onchange_price_subtotal()
            self._recompute_dynamic_lines(recompute_all_taxes=True)

    def update_discount(self):
        if self.type == 'out_invoice':
            order_id = self.env['sale.order'].search([('name','=',self.invoice_origin)],limit=1)
            # if order_id:
            #     self.discount_view = order_id.discount_view
            #     self.discount_type = order_id.discount_type
            #     self.discount_value = order_id.discount_value
            #     self.discounted_amount = order_id.discounted_amount



class account_move_line(models.Model):
    _inherit = 'account.move.line'

    discount_line = fields.Boolean('is a discount line')