# Copyright 2018 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    product_brand_id = fields.Many2one(
        comodel_name='product.brand',
        string='Brand',
    )
    product_model_id = fields.Many2one(
        'product.model',
        string='Model',
        help='Select a model for this product'
    )
    product_series_id = fields.Many2one(
        'product.series',
        string='Series',
        help='Select a series for this product'
    )
    production = fields.Many2one(
        'account.analytic.tag',
        string='Production',
    )
    product_group_id = fields.Many2one('product.category', string='Product Group')
    category_id = fields.Many2one('product.category', string='Product Category')
    sub_category_id = fields.Many2one('product.category', string='Product Sub Category')

    # pylint:disable=dangerous-default-value
    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['product_brand_id'] = ", t.product_brand_id as product_brand_id"
        fields['product_model_id'] = ", t.product_model_id as product_model_id"
        fields['product_series_id'] = ", t.product_series_id as product_series_id"

        fields['product_group_id'] = ", t.product_group_id as product_group_id"
        fields['category_id'] = ", t.category_id as category_id"
        fields['sub_category_id'] = ", t.sub_category_id as sub_category_id"
        groupby += ', t.product_brand_id, t.product_model_id, t.product_series_id'
        groupby += ', t.product_group_id, t.category_id, t.sub_category_id'
        return super(SaleReport, self)._query(
            with_clause, fields, groupby, from_clause
        )
