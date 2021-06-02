# -*- coding: utf-8 -*-
from odoo import fields, api, models, _

class ValuationProductTemplate(models.Model):
    _inherit = "stock.valuation.layer"

    categ_id = fields.Many2one('product.category', string='Product Category', related='product_id.categ_id', store=True)
    standard_price = fields.Float(string='Cost', related='product_id.standard_price')