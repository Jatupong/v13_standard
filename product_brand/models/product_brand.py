# Copyright 2009 NetAndCo (<http://www.netandco.net>).
# Copyright 2011 Akretion Benoît Guillot <benoit.guillot@akretion.com>
# Copyright 2014 prisnet.ch Seraphine Lantible <s.lantible@gmail.com>
# Copyright 2016 Serpent Consulting Services Pvt. Ltd.
# Copyright 2018 Daniel Campos <danielcampos@avanzosc.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models


class ProductBrand(models.Model):
    _name = 'product.brand'
    _description = "Product Brand"
    _order = 'name'

    name = fields.Char('Brand Name', required=True)
    description = fields.Text(translate=True)
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        help='Select a partner for this brand if any.',
        ondelete='restrict'
    )
    logo = fields.Binary('Logo File', attachment=True)
    product_ids = fields.One2many(
        'product.template',
        'product_brand_id',
        string='Brand Products',
    )
    products_count = fields.Integer(
        string='Number of products',
        compute='_compute_products_count',
    )

    @api.depends('product_ids')
    def _compute_products_count(self):
        for brand in self:
            brand.products_count = len(brand.product_ids)


class ProductModel(models.Model):
    _name = 'product.model'
    _description = "Product Model"
    _order = 'name'

    name = fields.Char('Model Name', required=True)
    description = fields.Text(translate=True)
    series_id = fields.Many2one('product.series', string='Series')

    product_ids = fields.One2many(
        'product.template',
        'product_model_id',
        string='Model Products',
    )
    products_count = fields.Integer(
        string='Number of products',
        compute='_compute_products_count',
    )


    @api.depends('product_ids')
    def _compute_products_count(self):
        for model in self:
            model.products_count = len(model.product_ids)


class ProductSeries(models.Model):
    _name = 'product.series'
    _description = "Product Series"
    _order = 'name'

    name = fields.Char('Series Name', required=True)
    description = fields.Text(translate=True)
    brand_id = fields.Many2one('product.brand',string='Brand')

    product_ids = fields.One2many(
        'product.template',
        'product_series_id',
        string='Series Products',
    )
    products_count = fields.Integer(
        string='Number of products',
        compute='_compute_products_count',
    )

    @api.depends('product_ids')
    def _compute_products_count(self):
        for series in self:
            series.products_count = len(series.product_ids)



class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_brand_id = fields.Many2one(
        'product.brand',
        string='Brand',
        help='Select a brand for this product'
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
