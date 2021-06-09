# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Book)

from odoo import fields, api, models, _
from odoo.exceptions import UserError, AccessError


class StockMove(models.Model):
    _inherit = 'stock.move'

    bom_id = fields.Many2one('mrp.bom', 'Bill of Material')

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        res = super(StockMove, self)._prepare_merge_moves_distinct_fields()
        res.append('name')

        return res

    @api.model
    def create(self, values):
        # print('StockMove create : ',values)
        bom_line_id = False
        if 'bom_line_id' in values:
            bom_line_id = self.env['mrp.bom.line'].browse(values.get('bom_line_id'))
        elif 'group_id' in values and 'bom_line_id' not in values:
            bom_line_id = self.env['stock.move'].search([('group_id', '=', values.get('group_id')),
                                                         ('bom_line_id', '!=', False),
                                                         ('sale_line_id', '!=', False),
                                                         ('product_id', '=', values.get('product_id')),
                                                         ], limit=1).mapped('bom_line_id')
        if bom_line_id:
            values.update({'bom_id': bom_line_id.bom_id.id})

        return super(StockMove, self).create(values)