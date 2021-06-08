# -*- coding: utf-8 -*-
# Copyright (c) 2015-Present TidyWay Software Solution. (<https://tidyway.in/>)

from odoo import fields, models, api
from odoo.exceptions import Warning
import odoo.addons.decimal_precision as dp


class BidLineQty(models.TransientModel):
    _name = "bid.line.qty"
    _description = "Change Bid line quantity"
    qty = fields.Float(
       string='Quantity',
       digits=dp.get_precision('Product Unit of Measure'),
       required=True
       )


    def change_qty(self):
        ctx = dict(self._context or {})
        purchase_ids = ctx and ctx.get('active_ids', [])
        if not purchase_ids:
            raise Warning(_('Purchase record not found!'))
        purchase_recs = self.env['purchase.order.line'].browse(purchase_ids)
        change_values = {
                         'quantity_bid': self.qty
                        }
        if self.qty < 0:
            raise Warning(_('Quantity must be positive.'))
        if self.qty == 0:
            change_values.update({
                                  'internal_state': 'draft'
                                  })
        else:
            change_values.update({
                                  'internal_state': 'positive'
                                  })
        purchase_recs.write(change_values)
