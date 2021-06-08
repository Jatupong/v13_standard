# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Book)

from odoo import fields, api, models, _


class AcoountMoveline(models.Model):
    _inherit = 'account.move.line'

    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    uom_class_ids = fields.Many2many('uom.uom', string='Unit of Measure (Class)', compute='_compute_uom_class')

    @api.depends('product_id', 'product_id.uom_class_ids')
    def _compute_uom_class(self):
        for obj in self:
            uom_class_ids = self.env['uom.uom']
            if obj.product_id:
                uom_class_ids = obj.product_id.uom_id
                if obj.product_id.uom_class_ids:
                    uom_class_ids |= obj.product_id.uom_class_ids
                elif obj.product_uom_category_id:
                    uom_class_ids |= self.env['uom.uom'].search([('category_id', '=', obj.product_uom_category_id.id)])

            obj.uom_class_ids = [(6, 0, uom_class_ids.ids)]

    @api.onchange('product_id')
    def _onchange_product_id(self):
        super(AcoountMoveline, self)._onchange_product_id()
        # print('def _onchange_product_id')
        uom_class_ids = self.env['uom.uom']
        for line in self:
            if not line.product_id or line.display_type in ('line_section', 'line_note'):
                continue
            
            if line.product_id:
                uom_class_ids = line.product_id.uom_id
                if line.product_id.uom_class_ids:
                    uom_class_ids |= line.product_id.uom_class_ids
                elif line.product_uom_id.category_id:
                    uom_class_ids |= self.env['uom.uom'].search([('category_id', '=', line.product_uom_id.category_id.id)])
        # print('uom_class_ids : ',uom_class_ids.mapped('name'))

        if len(self) == 1:
            return {'domain': {'product_uom_id': [('id', '=', uom_class_ids.ids)]}}