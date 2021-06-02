# -*- coding: utf-8 -*-
# Copyright (C) 2016-2017  Technaureus Info Solutions(<http://technaureus.com/>).

from odoo import api, models, fields, _
from odoo.exceptions import UserError
import pytz
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, timedelta, time as datetime_time

class StockCountWizard(models.TransientModel):
    _name = 'stock.count.wizard'

    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
    location_id = fields.Many2one('stock.location', string='Stock Location')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)

    product_id = fields.Many2one('product.product', string='Product')
    product_code_form = fields.Char(string='Product Code Form')
    product_code_to = fields.Char(string='Product Code To')

    product_form = fields.Many2one('product.product', string='Product Form')
    product_to = fields.Many2one('product.product', string='Product to')

    @api.onchange('product_form', 'product_to')
    def on_product_form_to(self):
        if self:
            self.product_code_form = self.product_form.default_code
            self.product_code_to = self.product_to.default_code

    @api.model
    def default_get(self, fields):
        res = super(StockCountWizard, self).default_get(fields)
        curr_date = datetime.now()
        from_date = datetime(curr_date.year, 1, 1).date() or False
        to_date = datetime(curr_date.year, curr_date.month, curr_date.day).date() or False
        res.update({'date_from': str(from_date), 'date_to': str(to_date)})

        return res

    def print_pdf_report(self, data):
        # print('print_pdf_report : ')
        data = {}
        data['form'] = self.read(['date_from', 'date_to', 'company_id', 'location_id', 'product_code_form', 'product_code_to'])[0]
        envref = self.env.ref('itaas_print_inventory_report.stock_count_report')
        # print('envref : ',envref)
        return envref.report_action(self, data=data,config=False)


class StockCountReport(models.AbstractModel):
    _name = 'report.itaas_print_inventory_report.stock_count_report_id'

    @api.model
    def get_report_values(self, docids, data=None):
        # print('get_report_values : ', docids, data)
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))

        company_id = self.env['res.company'].browse(data['form']['company_id'][0])
        # date_to_usertz = self.convert_utc_to_usertz(str2dt(data['form']['date_to']))
        date_to = fields.Date.from_string(data['form']['date_to'])
        date_to_usertz = datetime.combine(date_to, datetime_time.max)
        # print('date_to_utc : ', date_to_usertz)
        date_to_utc = self.convert_usertz_to_utc(date_to_usertz)
        date_to_utc = date_to_utc.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        # print('date_to_utc : ',date_to_utc)

        domain = [('in_date', '<=', date_to_utc)]
        if not data['form']['location_id']:
            domain.append(('location_id.usage', '=', 'internal'))
            # location_ids = self.env['stock.location'].search([('usage','=','internal')])
        else:
            domain.append(('location_id', '=', data['form']['location_id'][0]))
            # location_ids = self.env['stock.location'].search([('id', '=', data['form']['location_id'][0])])

        if data['form']['product_code_form'] and data['form']['product_code_to']:
            domain.append(('product_id.default_code', '>=', str(data['form']['product_code_form'])))
            domain.append(('product_id.default_code', '<=', str(data['form']['product_code_to'])))

        stock_quant_ids = self.env['stock.quant'].search(domain)
        location_ids = stock_quant_ids.mapped('location_id')
        if not stock_quant_ids:
            raise UserError(_('Document is empty.'))

        # print('stock_quant_ids : ',stock_quant_ids.mapped('in_date'))

        docargs = {
            'doc_ids': docids,
            'data': data['form'],
            'docs': docs,
            'date_from': data['form']['date_from'],
            'date_to': data['form']['date_to'],
            'company_id': company_id,
            'location_ids': location_ids,
            'stock_quant_ids': stock_quant_ids,
        }
        return docargs

    def convert_usertz_to_utc(self, date_time):
        user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
        # print('user_tz : ',user_tz)
        tz = pytz.timezone('UTC')
        date_time = user_tz.localize(date_time).astimezone(tz)
        # print('date_time : ')
        # date_time = date_time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        return date_time