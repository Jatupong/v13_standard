# -*- coding: utf-8 -*-
# Copyright (C) 2016-2017  Technaureus Info Solutions(<http://technaureus.com/>).

import base64
import xlwt
from io import StringIO

from datetime import datetime,date
from openerp import models, fields, api, _
from openerp.exceptions import UserError
from openerp.tools import misc

def strToDate(dt):
    return date(int(dt[0:4]), int(dt[5:7]), int(dt[8:10]))


# this is for tax report section
class PND53_Report(models.TransientModel):
    _inherit = 'pnd53.report'

    @api.multi
    def get_bank_report(self):

        context = dict(self._context or {})
        file_type = context.get('file')

        fl = StringIO()
        workbook = xlwt.Workbook(encoding='utf-8')

        font = xlwt.Font()
        font.bold = True
        font.bold = True
        for_right = xlwt.easyxf(
            "font: name  Times New Roman,color black,  height 180;  align: horiz right,vertical center; borders: top thin, bottom thin, left thin, right thin")
        for_right.num_format_str = '#,###.00'
        for_right_bold = xlwt.easyxf(
            "font: bold 1, name  Times New Roman,color black,  height 180;  align: horiz right,vertical center; borders: top thin, bottom thin, left thin, right thin")
        for_right_bold.num_format_str = '#,###.00'
        for_center = xlwt.easyxf(
            "font: name  Times New Roman, color black,  height 180; align: horiz center,vertical center,wrap on; borders: top thin, bottom thin, left thin, right thin")
        for_left = xlwt.easyxf(
            "font: name  Times New Roman,color black,  height 180;  align: horiz left,vertical center; borders: top thin, bottom thin, left thin, right thin")
        for_center_bold = xlwt.easyxf(
            "font: bold 1, name  Times New Roman, color black, height 180;  align: horiz center,vertical center,wrap on; borders: top thin, bottom thin, left thin, right thin")
        for_left_bold_no_border = xlwt.easyxf(
            "font: bold 1, name  Times New Roman, color black, height 180;  align: horiz left,vertical center;")

        GREEN_TABLE_HEADER = xlwt.easyxf(
            'font: bold 1, name  Times New Roman, height 300,color black;'
            'align: vertical center, horizontal center, wrap on;'
            'borders: top thin, bottom thin, left thin, right thin;'
            'pattern:  pattern_fore_colour white, pattern_back_colour white'
        )

        alignment = xlwt.Alignment()  # Create Alignment
        alignment.horz = xlwt.Alignment.HORZ_RIGHT
        style = xlwt.easyxf('align: wrap yes')
        style.num_format_str = '#,###.00'
        cr, uid, context = self.env.args
        final_text = ""
        final_text_body = ""

        # -------------------------------------- PND 3 ----------------------------------------
        if self.report_type == 'personal':

            # worksheet = workbook.add_sheet('report')
            # worksheet_detail = workbook.add_sheet('report_detail')

            move_line_ids = self.env['account.move.line'].search(
                [('date_maturity', '>=', self.date_from), ('date_maturity', '<=', self.date_to),
                 ('wht_personal_company', '=', 'personal'), ('wht_type', '!=', False)], order='date_maturity,wht_reference ASC')
            move_ids = ""
            inv_row = 1
            for move in move_line_ids:
                move_ids += str(inv_row)  + '|'
                move_ids += str(move.partner_id.vat) + '|'
                move_ids += str(move.partner_id.title.name) + '|'

                name_temp = move.partner_id.name.split(' ')
                if len(name_temp) > 2:
                    first_name = name_temp[0]
                    last_name = name_temp[1]
                else:
                    first_name = name_temp[0]
                    last_name = " "

                move_ids += str(first_name) + '|'
                move_ids += str(last_name) + '|'
                if move.partner_id.street:
                    move_ids += str(move.partner_id.street)
                if move.partner_id.street2:
                    move_ids += str(move.partner_id.street2)
                if move.partner_id.city:
                    move_ids += str(move.partner_id.city)
                if move.partner_id.city:
                    move_ids += str(move.partner_id.city)
                if move.partner_id.state_id and move.partner_id.state_id.name:
                    move_ids += str(move.partner_id.state_id.name)
                if move.partner_id.zip:
                    move_ids += str(move.partner_id.zip)

                move_ids += '|'

                move_ids += strToDate(move.date_maturity).strftime("%d/%m/%y") + '|'
                move_ids += str(move.name) + '|'

                if move.wht_type:
                    if move.wht_type == '1%':
                        wht_type = '1'
                    elif move.wht_type == '2%':
                        wht_type = '2'
                    elif move.wht_type == '3%':
                        wht_type = '3'
                    elif move.wht_type == '5%':
                        wht_type = '5'

                move_ids += str(wht_type) + '|'
                move_ids += str(move.amount_before_tax) + '|'
                move_ids += str(move.credit) + '|'
                move_ids += '1' + "\n"

                # worksheet.write(inv_row, 0, move_ids, for_left)
                final_text = final_text_body + str(move_ids)

                inv_row += 1


        # ------------------------------------ End PND 3 -------------------------------------------------

        # -------------------------------------- PND 53 ----------------------------------------
        elif self.report_type == 'company':

            # worksheet = workbook.add_sheet('report')
            # worksheet_detail = workbook.add_sheet('report_detail')

            move_line_ids = self.env['account.move.line'].search(
                [('date_maturity', '>=', self.date_from), ('date_maturity', '<=', self.date_to),
                 ('wht_personal_company', '=', 'company'), ('wht_type', '!=', False)], order='date_maturity,wht_reference ASC')
            move_ids = ""
            inv_row = 1
            for move in move_line_ids:
                move_ids += str(inv_row) + '|'
                move_ids += str(move.partner_id.vat) + '|'
                move_ids += 'บริษัท' + '|'
                move_ids += str(move.partner_id.name) + '|'

                if move.partner_id.street:
                    move_ids += str(move.partner_id.street)
                if move.partner_id.street2:
                    move_ids += str(move.partner_id.street2)
                if move.partner_id.city:
                    move_ids += str(move.partner_id.city)
                if move.partner_id.city:
                    move_ids += str(move.partner_id.city)
                if move.partner_id.state_id and move.partner_id.state_id.name:
                    move_ids += str(move.partner_id.state_id.name)
                if move.partner_id.zip:
                    move_ids += str(move.partner_id.zip)

                move_ids +='|'
                move_ids += strToDate(move.date_maturity).strftime("%d/%m/%Y") + '|'
                move_ids += str(move.name) + '|'

                if move.wht_type:
                    if move.wht_type == '1%':
                        wht_type = '1'
                    elif move.wht_type == '2%':
                        wht_type = '2'
                    elif move.wht_type == '3%':
                        wht_type = '3'
                    elif move.wht_type == '5%':
                        wht_type = '5'

                move_ids += str(wht_type) + '|'
                move_ids += str(move.amount_before_tax) + '|'
                move_ids += str(move.credit) + '|'
                move_ids += '1' + "\n"

                # worksheet.write(inv_row, 0, move_ids, for_left)
                final_text = final_text_body + str(move_ids)

                inv_row += 1


        # ------------------------------------ End PND 53 -------------------------------------------------

        else:
            raise UserError(_('There is record this date range.'))

        values = {
            'name': "Witholding Report",
            'datas_fname': 'witholding_report.txt',
            'res_model': 'ir.ui.view',
            'res_id': False,
            'type': 'binary',
            'public': True,
            'datas': base64.b64encode((final_text).encode("utf-8")),
        }
        attachment_id = self.env['ir.attachment'].sudo().create(values)
        download_url = '/web/content/' + str(attachment_id.id) + '?download=True'
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')

        return {
            "type": "ir.actions.act_url",
            "url": str(base_url) + str(download_url),
            "target": "new",
        }
