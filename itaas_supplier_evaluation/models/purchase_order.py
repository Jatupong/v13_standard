# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Book)

from datetime import datetime, timedelta, date
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    evaluation_ids = fields.One2many('stock.evaluation', 'purchase_id', string='Evaluation', copy=False, readonly=1)
    score_evaluation = fields.Float(string='Score Evaluation', compute='_compute_score_evaluation')

    @api.depends('evaluation_ids')
    def _compute_score_evaluation(self):
        # print('_compute_score_evaluation')
        for odj in self:
            # print('evaluation_ids : ',odj.evaluation_ids)
            if odj.evaluation_ids:
                score_evaluation = odj.evaluation_ids.mapped('score_total')
                # print('score_evaluation : ', odj.evaluation_ids)
                odj.update({'score_evaluation':score_evaluation})
