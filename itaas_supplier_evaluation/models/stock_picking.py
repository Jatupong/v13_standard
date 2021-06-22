# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Book)

from odoo import fields, api, models, _
from bahttext import bahttext
from odoo.exceptions import UserError
from datetime import datetime, date

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    evaluation_ids = fields.One2many('stock.evaluation', 'picking_id', string='Evaluation', copy=False, auto_join=True)

    def action_done(self):
        res = super(StockPicking, self).action_done()
        if self.picking_type_code == 'incoming' and not self.evaluation_ids:
            self.create_stock_evaluation()
        return res

    def create_stock_evaluation(self):
        print('def create_stock_evaluation')
        type_ids = self.env['stock.evaluation.type'].sudo().search([])
        qty_done = sum(self.move_lines.mapped('quantity_done'))

        if not self.evaluation_ids:
            evaluation_ids = []
            for type in type_ids:
                score = type.score
                val = {'picking_id':self.id,
                       'partner_id': self.partner_id.id,
                       'purchase_id': self.purchase_id.id,
                       'type_id' : type.id,
                       'score': score,
                       'score_deduct': 0.0,
                       'score_total': score,}
                evaluation_ids.append((0,0,val))
            self.update({'evaluation_ids':evaluation_ids})
        else:
            for line in self.evaluation_ids:
                type_id = self.env['stock.evaluation.type'].sudo().search([('id','=',line.type_id.id)], limit = 1)
                score = type_id.score
                val = {'date_evaluation': date.today(),
                       'partner_id': self.partner_id.id,
                       'purchase_id': self.purchase_id.id,
                       'score': score,
                       'score_deduct': 0.0,
                       'score_total': score,
                       }
                line.update(val)