# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Book)

from odoo import fields, api, models, _

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    uom_category_id = fields.Many2one('uom.category', 'Uom Category', related='uom_id.category_id')
    uom_class_ids = fields.Many2many('uom.uom', 'uom_class_ref', domain="[('category_id','=',uom_category_id)]", string='Unit of Measure (Class)')

    uom_po_category_id = fields.Many2one('uom.category', 'Purchase Uom Category', related='uom_po_id.category_id')
    uom_po_class_ids = fields.Many2many('uom.uom', 'uom_po_class_ref', domain="[('category_id','=',uom_po_category_id)]", string='Purchase Unit of Measure (Class)')