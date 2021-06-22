# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Book)

from odoo import fields, api, models, _
from bahttext import bahttext
from odoo.exceptions import UserError
from datetime import datetime, date

class StockEvaluation(models.Model):
    _name = 'stock.evaluation'
    _rec_name = 'picking_id'
    _order = 'date_evaluation desc'

    picking_id = fields.Many2one('stock.picking', string='Picking Reference', ondelete='cascade', copy=False)
    picking_state = fields.Selection(copy=False, default='draft', string='Status',related='picking_id.state')
    purchase_id = fields.Many2one('purchase.order', string='Purchase Reference', copy=False)
    partner_id = fields.Many2one('res.partner', string="Vendor")
    type_id = fields.Many2one('stock.evaluation.type', string='Type', required=True)
    score = fields.Float(String="Score")
    date_evaluation = fields.Date(string="Date", default=fields.Date.today())
    # -----------------------------------
    score_deduct = fields.Float(String="Score Deduct")
    # -----------------------------------
    score_total = fields.Float(String="Score Total", store=True, readonly=True, compute='_score_all')
    description = fields.Char(string='Description')
    #-----------------------------------

    @api.onchange('type_id',)
    def onchange_type(self):
        if self.type_id:
            self.score = self.type_id.score

    @api.depends('score','score_deduct')
    def _score_all(self):
        for obj in self:
            score_total = obj.score - obj.score_deduct
            obj.update({'score_total': score_total,})


class StockEvaluationType(models.Model):
    _name = 'stock.evaluation.type'
    _rec_name = 'name'

    name = fields.Text(string='Name', required=True, translate=True)
    score = fields.Float(String="Score")
    sequence = fields.Integer(string='Sequence')
    description = fields.Char(string='Description')


class score_grade(models.Model):
    _name = 'stock.score.grade'
    _rec_name = 'name'
    _order = "max_score desc"

    name = fields.Text(string='Name' ,required=True)
    min_score = fields.Integer(string='Min score' ,required=True)
    max_score = fields.Integer(string='Max score' ,required=True)
    result = fields.Selection([('pass', 'Pass'), ('fail', 'Fail'), ], string='Result', default='pass', required=True)
    description = fields.Char(string='Description')

    _sql_constraints = [('min_score_uniq', 'unique(min_score)', 'Min score of the Score levels must be different'),
                        ('max_score_uniq', 'unique(max_score)', 'Max score of the Score levels must be different')]

    def name_get(self):
        result = []
        for obj in self:
            if obj.name:
                name = obj.name
            result.append((obj.id, name))

        return result