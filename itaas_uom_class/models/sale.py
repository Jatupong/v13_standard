# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Book)

from odoo import fields, api, models, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    uom_class_ids = fields.Many2many('uom.uom', string='Unit of Measure (Class)', compute='_compute_uom_class')

    @api.depends('product_id')
    def _compute_uom_class(self):
        # print('def _compute_uom_class')
        for obj in self:
            uom_class_ids = self.env['uom.uom']
            if obj.product_id:
                uom_class_ids = obj.product_id.uom_id
                if obj.product_id.uom_class_ids:
                    uom_class_ids |= obj.product_id.uom_class_ids
                elif obj.product_uom_category_id:
                    uom_class_ids |= self.env['uom.uom'].search([('category_id', '=', obj.product_uom_category_id.id)])

            obj.uom_class_ids = [(6, 0, uom_class_ids.ids)]