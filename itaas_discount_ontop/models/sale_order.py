# -*- coding: utf-8 -*-
from odoo import fields, api, models, _
import math

from odoo.tools import float_round


class SaleOrderLine(models.Model):
    _inherit ="sale.order.line"

    discount_ontop1 = fields.Float('Ontop 1', digits='Discount')
    discount_ontop2 = fields.Float('Ontop 2', digits='Discount')
    discount_ontop3 = fields.Float('Ontop 3', digits='Discount')

    def _prepare_invoice_line(self):
        res = super(SaleOrderLine, self)._prepare_invoice_line()
        ori_price = self.price_unit
        price = self.price_unit
        numbe_text = ''
        if self.discount:
            price = price * (1 - (self.discount or 0.0) / 100.0)
            numbe_text += str(int(self.discount)) + '%'
        if self.discount_ontop1:
            price = price * (1 - (self.discount_ontop1 or 0.0) / 100.0)
            numbe_text +=  str(int(self.discount_ontop1)) + '%'
        if self.discount_ontop2:
            price = price * (1 - (self.discount_ontop2 or 0.0) / 100.0)
            numbe_text +=  ',' + str(int(self.discount_ontop2)) + '%'
        if self.discount_ontop3:
            price = price * (1 - (self.discount_ontop3 or 0.0) / 100.0)
            numbe_text += ',' + str(int(self.discount_ontop3)) + '%'
        if ori_price:
            ontop = (ori_price - price) * 100 / ori_price
            ontop = round(ontop, 2)
            res.update({'discount': ontop,
                        'numbe_text':numbe_text
                        })
        return res

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id','discount_ontop1','discount_ontop2','discount_ontop3')
    def _compute_amount(self):
        super(SaleOrderLine, self)._compute_amount()
        for line in self:

            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            if line.discount_ontop1:
                price = price * (1 - (line.discount_ontop1 or 0.0) / 100.0)
            if line.discount_ontop2:
                price = price * (1 - (line.discount_ontop2 or 0.0) / 100.0)
            if line.discount_ontop3:
                price = price * (1 - (line.discount_ontop3 or 0.0) / 100.0)

            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })




