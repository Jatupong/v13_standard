# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Book)

from datetime import datetime, timedelta, date
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class StockEvaluationReport(models.Model):
    _name = 'stock.evaluation.report'
    _rec_name = 'partner_id'
    _order = 'id desc'

    date_from = fields.Date(string='Date From', required="1")
    date_to = fields.Date(string='Date To', required="1")
    partner_id = fields.Many2one('res.partner', string='Partner', required="1",)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    # ----------------------------------------------------------------------
    product_quality_vendor = fields.Text('Product Quality' , translate=True)
    delivery_vendor = fields.Text('Delivery', translate=True)
    responsibility_vendor = fields.Text('Responsibility', translate=True)
    service_price_vendor = fields.Text('Service / Price', translate=True)
    evaluation_remark_vendor = fields.Text('Remark', translate=True)
    # ----------------------------------------------------------------------
    product_quality_company = fields.Text('Product Quality', translate=True)
    delivery_company = fields.Text('Delivery', translate=True)
    responsibility_company = fields.Text('Responsibility', translate=True)
    service_price_company = fields.Text('Service / Price', translate=True)
    evaluation_remark_company = fields.Text('Remark', translate=True)
    # ----------------------------------------------------------------------
    # evaluation_ids = fields.Many2many('stock.evaluation', string='Evaluation', compute='_compute_get_evaluation_range',)
    # score = fields.Float(String="Score", store=True, compute='_compute_get_evaluation_range',)
    # score_deduct = fields.Float(String="Score Deduct", store=True, compute='_compute_get_evaluation_range',)
    # score_total = fields.Float(String="Score Total", store=True, compute='_compute_get_evaluation_range',)
    # score_grade = fields.Many2one('stock.score.grade',String="Grade", store=True, compute='_compute_get_evaluation_range',)
    evaluate_by = fields.Many2one('res.users', string='Evaluate By', default=lambda self: self.env.uid)
    evaluate_date = fields.Date(string="Evaluate Date", default=fields.Date.today())
    validate_by = fields.Many2one('res.users', string='Validate By', readonly=True)
    validate_date = fields.Date(string="Validate Date", default=fields.Date.today())
    # ----------------------------------------------------------------------
    state = fields.Selection([('draft', 'Draft'), ('accept', 'Accept'), ('not_accept', 'Not Accept'),], string='Status',
                             readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

    remark = fields.Text('Remark', translate=True)
    within_day = fields.Integer(string='Within day' ,default=15)

    @api.model
    def default_get(self, fields):
        res = super(StockEvaluationReport, self).default_get(fields)
        curr_date = datetime.now()
        from_date = datetime(curr_date.year, 1, 1).date() or False
        to_date = datetime(curr_date.year, curr_date.month, curr_date.day).date() or False
        res.update({'date_from': str(from_date), 'date_to': str(to_date)})
        return res

    # @api.depends('date_from','date_to','partner_id')
    # def _compute_get_evaluation_range(self):
    #     # print('def _compute_get_evaluation_range')
    #     for obj in self:
    #         stock_evaluation = self.env['stock.evaluation'].sudo().search([('partner_id', '=', obj.partner_id.id),
    #                                                                        ('date_evaluation', '>=', obj.date_from),
    #                                                                        ('date_evaluation', '<=', obj.date_to), ])
    #         if stock_evaluation:
    #             get_score = obj.get_score_vender_date(stock_evaluation)
    #             score = get_score['score']
    #             score_deduct = get_score['score_deduct']
    #             score_total = get_score['score_total']
    #             score_grade = get_score['score_grade']
    #             obj.update({'evaluation_ids': [(6, 0, stock_evaluation.ids)],
    #                         'score': score,
    #                         'score_deduct': score_deduct,
    #                         'score_total': score_total,
    #                         'score_grade': score_grade, })

    def get_evaluation_range(self, date_from, date_to, partner_id):

        stock_evaluation = self.env['stock.evaluation'].sudo().search([('partner_id', '=', partner_id.id),
                                                                       ('date_evaluation', '>=', date_from),
                                                                       ('date_evaluation', '<=', date_to), ])
        if not stock_evaluation:
            raise UserError(_('Empty Document'))

        return stock_evaluation


    def get_score_vender_date(self, stock_evaluation):
        print('get_score_vender_date : ',stock_evaluation)
        # print('def get_score_vender assessment_result_report_id')
        score = score_deduct = 0
        if stock_evaluation:
            len_stock = len(stock_evaluation.mapped('picking_id'))
            print('len_stock : ',len_stock)
            score = sum(stock_evaluation.mapped('score')) / len_stock
            score_deduct = sum(stock_evaluation.mapped('score_deduct')) / len_stock
            score_total = score - score_deduct
            print('score : ',score)
            print('score_deduct : ',score_deduct)
            print('score_total : ',score_total)
            score_grade = self.env['stock.score.grade'].sudo().search([('max_score', '>=', score_total)], limit=1,
                                                                      order='max_score asc')

        return {'score': score,
                'score_deduct': score_deduct,
                'score_total': score_total,
                'score_grade': score_grade.id or False,}

    def action_accept(self):
        self.write({'state': 'accept',
                    'validate_by': self.env.uid,
                    'validate_date': datetime.today(),})

    def action_not_accept(self):
        self.write({'state':'not_accept',
                    'validate_by': self.env.uid,
                    'validate_date': datetime.today(),})

    def action_draft(self):
        self.write({'state':'draft',})


class score_grade(models.Model):
    _name = 'stock.score.grade'
    _rec_name = 'name'
    _order = "max_score desc"

    name = fields.Text(string='Name' ,required=True)
    min_score = fields.Integer(string='Min score' ,required=True)
    max_score = fields.Integer(string='Max score' ,required=True)
    result = fields.Selection([('pass', 'Pass'), ('not', 'Not'), ], string='Result', default='pass', required=True)
    description = fields.Char(string='Description')

    _sql_constraints = [('min_score_uniq', 'unique(min_score)', 'Min score of the Score levels must be different'),
                        ('max_score_uniq', 'unique(max_score)', 'Max score of the Score levels must be different')]

    @api.depends('name')
    def name_get(self):
        result = []
        for obj in self:
            if obj.name:
                name = obj.name
            result.append((obj.id, name))

        return result