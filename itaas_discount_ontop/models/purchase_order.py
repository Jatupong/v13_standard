# -*- coding: utf-8 -*-
from odoo import fields, api, models, _


class PurchaseOrderLine(models.Model):
    _inherit ="purchase.order.line"

    discount_ontop1 = fields.Float('Ontop 1', digits='Discount')
    discount_ontop2 = fields.Float('Ontop 2', digits='Discount')
    discount_ontop3 = fields.Float('Ontop 3', digits='Discount')

    def _prepare_account_move_line(self, move):
        res = super(PurchaseOrderLine, self)._prepare_account_move_line(move)
        ori_price = self.price_unit
        price = self.price_unit
        numbe_text = ''
        if self.discount:
            price = price * (1 - (self.discount or 0.0) / 100.0)
            numbe_text += str(int(self.discount)) + '%'
        if self.discount_ontop1:
            price = price * (1 - (self.discount_ontop1 or 0.0) / 100.0)
            numbe_text +=   str(int(self.discount_ontop1)) + '%'
        if self.discount_ontop2:
            price = price * (1 - (self.discount_ontop2 or 0.0) / 100.0)
            numbe_text += ',' + str(int(self.discount_ontop2)) + '%'
        if self.discount_ontop3:
            price = price * (1 - (self.discount_ontop3 or 0.0) / 100.0)
            numbe_text += ',' + str(int(self.discount_ontop3)) + '%'
        if ori_price:
            ontop = (ori_price - price) * 100 / ori_price
            ontop = round(ontop, 2)

            res.update({'discount': ontop,
                        'numbe_text': numbe_text
                        })
        return res

    @api.depends('product_qty', 'price_unit', 'taxes_id','discount_ontop1','discount_ontop2','discount_ontop3')
    def _compute_amount(self):
        super(PurchaseOrderLine, self)._compute_amount()
        for line in self:
            vals = line._prepare_compute_all_values()
            price = vals['price_unit']
            if line.discount_ontop1:
                price = price * (1 - (line.discount_ontop1 or 0.0) / 100.0)
            if line.discount_ontop2:
                price = price * (1 - (line.discount_ontop2 or 0.0) / 100.0)
            if line.discount_ontop3:
                price = price * (1 - (line.discount_ontop3 or 0.0) / 100.0)

            vals['price_unit'] = price
            taxes = line.taxes_id.compute_all(vals['price_unit'],
                                              vals['currency_id'],
                                              vals['product_qty'],
                                              vals['product'],
                                              vals['partner'])

            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
