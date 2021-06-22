# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Book)

from datetime import datetime
from odoo import tools
# from odoo import api, fields, models, _
from odoo.tools.translate import _
from odoo import api, models, fields, _
import xlwt
import time
import xlsxwriter
import base64
from datetime import datetime, date
from odoo.exceptions import UserError
from odoo.tools import misc
import operator
import locale
from odoo.tools import float_compare, float_is_zero
from dateutil.relativedelta import relativedelta
import calendar

def strToDate(dt):
    return date(int(dt[0:4]), int(dt[5:7]), int(dt[8:10]))

class wizard_stock_evaluation(models.TransientModel):
    _name = 'wizard.stock.evaluation'

    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    year = fields.Char(string='Year')
    total_supplier_ids = fields.Many2many('res.partner','stock_supplier_ids', string='Total Partner',store=True)
    partner_ids = fields.Many2many('res.partner','stock_partner_ids', string='Partner', store=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    evaluate_by = fields.Many2one('res.users', string='Evaluate By', default=lambda self: self.env.uid)
    evaluate_date = fields.Date(string="Evaluate Date", default=fields.Date.today())
    validate_by = fields.Many2one('res.users', string='Validate By', default=lambda self: self.env.uid)

    @api.onchange('year','date_from','date_to')
    def _get_total_supplier(self):
        # print("def _get_total_supplier")
        for odj in self:
            year = odj.year
            try:
                year_int = int(year)
            except ValueError:
                raise UserError(_('Please Check Year!'))
            date_from = str(year) + '-01-01'
            date_to = str(year) + '-12-31'

            evaluation_ids = odj.env['stock.evaluation'].search([('date_evaluation', '>=', date_from),
                                                                 ('date_evaluation', '<=', date_to)])
            supplier_ids = []
            partner_evaluation_ids =  evaluation_ids.mapped('partner_id')
            if partner_evaluation_ids:
                for partner in partner_evaluation_ids:
                    if partner.id not in supplier_ids:
                        supplier_ids.append(partner.id)
                odj.update({
                    'total_supplier_ids': [(6, 0, supplier_ids)],
                })

    @api.model
    def default_get(self, fields):
        res = super(wizard_stock_evaluation, self).default_get(fields)
        curr_date = datetime.now()
        year = str(curr_date.year)
        res.update({'year':year,})
        return res

    def _prepare_report_data(self):
        data = {
            'year': self.year,
            'partner_ids': self.partner_ids.ids,
            'company_id': self.company_id,
            'evaluate_by': self.evaluate_by,
            'evaluate_date': self.evaluate_date,
            'validate_by': self.validate_by,
            'date_from': self.date_from,
            'date_to': self.date_to,
        }
        return data

    def print_pdf_report(self):
        data = self._prepare_report_data()
        return self.env.ref('itaas_supplier_evaluation.summary_stock_evaluation').report_action(self, data=data)

    def get_score_vender_evaluation(self, partner):
        # print('def get_score_vender_evaluation')
        evaluation = []
        domain = [('partner_id', '=', partner.id),('date_evaluation', '>=', self.date_from),('date_evaluation', '<=', self.date_to)]
        # print('domain : ',q + 1,' : ',domain)
        evaluation_ids = self.env['stock.evaluation'].sudo().search(domain)
        print('evaluation_ids:',evaluation_ids)
        if evaluation_ids:
            picking_len = len(evaluation_ids.mapped('picking_id'))
            evaluation_len = len(evaluation_ids)
            score = sum(evaluation_ids.mapped('score')) / picking_len
            score_evaluation = sum(evaluation_ids.mapped('score_total')) / picking_len
            print('score:',score)
            print('score_evaluation:',score_evaluation)
            evaluation.append({
                               'score': score,
                               'score_evaluation': score_evaluation,
                               'evaluation_len': evaluation_len,
                               'evaluation_ids': evaluation_ids,
                               'has_data': True})
            print('score : ', score)
        else:
            evaluation.append({
                               'score': 0,
                               'score_evaluation': 0,
                               'evaluation_len': 0,
                               'has_data': False})
        print('evaluation : ',evaluation)
        return evaluation


class summary_stock_evaluation_report(models.AbstractModel):
    _name = 'report.itaas_supplier_evaluation.summary_stock_evaluation_id'

    @api.model
    def _get_report_values(self, docids, data=None):
        # print('def get_report_values : ',self.env.context)
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        # print('docs : ',docs)
        print('data:',data)
        doc_model = 'stock.evaluation'
        domain = []
        if data:
            date_from = data['date_from']
            date_to = data['date_to']

            domain.append(('date_evaluation', '>=', date_from))
            domain.append(('date_evaluation', '<=', date_to))
            if data['partner_ids']:
                partner_ids = data['partner_ids']
                domain.append(('partner_id', 'in', partner_ids))
        # print('domain : ',domain)
        evaluation_ids = self.env['stock.evaluation'].search(domain)
        if not evaluation_ids:
            raise UserError(_('There is record this date range.'))

        supplier_ids = evaluation_ids.mapped('partner_id')

        docargs = {
            'doc_ids': docids,
            'doc_model': doc_model,
            'data': data,
            'docs': docs,
            'evaluation_ids': evaluation_ids,
            'supplier_ids': supplier_ids,
            'date_from': date_from,
            'date_to': date_to,
        }
        return docargs







