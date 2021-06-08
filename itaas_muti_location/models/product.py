# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Book)

from odoo import fields, api, models, _
from bahttext import bahttext
from odoo.exceptions import UserError
from datetime import datetime, date

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    location_ids = fields.Many2many('stock.location', 'location_product_ref', string="Muti Location")