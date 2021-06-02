# -*- coding: utf-8 -*-


from odoo import api, fields, models, _


class StockQuantityHistory(models.TransientModel):
    _name = 'stock.product.quantity.overview'
    _description = 'Stock Product Quantity Overview'

    
    product_id = fields.Many2one("product.product", string="Product", required=True, domain=[('type', '=', 'product')])
    
    
    def stock_product_overview(self):
        self.ensure_one()
        sel_product_id = self.product_id.id
        self.env['stock.quant']._merge_quants()
        self.env['stock.quant']._unlink_zero_quants()
        return {'domain': "[('product_id', '=', %s)]" %sel_product_id,
                    'name': _("Stock Product Quantity Overview"),
                    'view_mode': 'tree,form,pivot',
                    'auto_search': True,
                    'res_model': 'stock.quant',
                    'view_id': False,
                    'context' : {'search_default_internal_loc': 1, 'search_default_transit_loc': 1},
                    'type': 'ir.actions.act_window'}