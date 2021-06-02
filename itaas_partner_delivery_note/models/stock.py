# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Book)


from odoo import api, fields, models, _
from odoo.exceptions import UserError

class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_new_picking_values(self):
        vals = super(StockMove, self)._get_new_picking_values()
        note_for_delivery = self.mapped('sale_line_id.order_id').filtered(lambda l: l.note_for_delivery).mapped('note_for_delivery')
        if note_for_delivery:
            vals['note'] = '\n'.join(note_for_delivery)

        return vals

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    description_move = fields.Char('Description', related='move_id.name')