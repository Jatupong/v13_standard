# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Book)

from odoo import fields, api, models, _


class PurchaseRequestLine(models.Model):
    _inherit = 'purchase.request.line'

    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    uom_class_ids = fields.Many2many('uom.uom', string='Unit of Measure (Class)', compute='_compute_uom_class')

    @api.depends('product_id', 'product_id.uom_class_ids')
    def _compute_uom_class(self):
        for obj in self:
            uom_class_ids = self.env['uom.uom']
            if obj.product_id:
                if obj.product_id.uom_po_id:
                    uom_class_ids |= obj.product_id.uom_po_id
                else:
                    uom_class_ids |= obj.product_id.uom_id
                if obj.product_id.uom_class_ids:
                    uom_class_ids |= obj.product_id.uom_class_ids
                elif obj.product_uom_category_id:
                    uom_class_ids |= self.env['uom.uom'].search([('category_id', '=', obj.product_uom_category_id.id)])

            obj.uom_class_ids = [(6, 0, uom_class_ids.ids)]