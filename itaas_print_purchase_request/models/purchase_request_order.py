# -*- coding: utf-8 -*-
from odoo import fields, api, models, _
from bahttext import bahttext
import math
from bahttext import bahttext
from num2words import num2words
import locale
from odoo.exceptions import UserError
from datetime import datetime, date

from odoo import api, fields, models, _
from datetime import datetime, date
import dateutil.parser
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT,DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_is_zero, float_compare
from datetime import datetime, timedelta

class purchase_request(models.Model):
    _inherit = "purchase.request"

    department_id = fields.Many2one('hr.department', string='แผนก')

    # @api.multi
    def action_rfq_send(self):
        '''
        This function opens a window to compose an email, with the edi purchase template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            if self.env.context.get('send_rfq', False):
                template_id = ir_model_data.get_object_reference('purchase', 'purchase.email_template_edi_purchase')[1]
            else:
                template_id = ir_model_data.get_object_reference('itaas_print_purchase_report',
                                                                 'new_email_template_edi_purchase_done')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(self.env.context or {})
        ctx.update({
            'default_model': 'purchase.order',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'custom_layout': "purchase.mail_template_data_notification_email_purchase_order",
            'purchase_mark_rfq_sent': True,
            'force_email': True
        })
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    def get_lines(self, data, max_line):
        # this function will count number of \n
        # print  data
        line_count = data.count("\n")
        # print (line_count)
        # print (max_line)
        if not line_count:
            # print ("line 0 - no new line or only one line")

            # lenght the same with line max
            if not len(data) % max_line:
                line_count = len(data) / max_line
            # lenght not the same with line max
            # if less than line max then will be 0 + 1
            # if more than one, example 2 line then will be 1 + 1
            else:
                # print (len(data))
                line_count = len(data) / max_line
                line_count = math.ceil(line_count)
                # roundup(line_count)
                # line_count = len(data) / max_line + 1
        elif line_count:
            # print ("line not 0 - has new line")
            # print line_count
            # if have line count mean has \n then will be add 1 due to the last row have not been count \n
            line_count += 1
            data_line_s = data.split('\n')
            for x in range(0, len(data_line_s), 1):
                # print data_line_s[x]
                if len(data_line_s[x]) > max_line:
                    # print "more than one line"
                    line_count += len(data_line_s[x]) / max_line
        # print("final line")
        # print(line_count)
        if line_count > 1:
            line_count = line_count * 0.8
        return line_count

    def get_break_line(self, max_body_height, new_line_height, row_line_height, max_line_lenght):
        break_page_line = []
        count_height = 0
        count = 1

        for line in self.line_ids:
            line_name = self.get_lines(line.name, max_line_lenght)
            line_height = row_line_height * line_name
            # print (line_height)

            ##############
            count_height += line_height
            # print ('COUNT-H')
            # print (count_height)
            # print (max_body_height)
            if count_height > max_body_height:
                # print ('OVER H')
                break_page_line.append(count - 1)
                count_height = line_height
            count += 1
        # last page
        break_page_line.append(count - 1)
        return break_page_line

    def get_pr_id(self):
        pr_id = self.order_line.filtered(lambda x: x.pr_id)

        if pr_id:
            word = ""
            for line in pr_id:
                word = word + line.pr_id.name
            return word
        else:
            return False


    # def baht_text(self, amount_total):
    #     return bahttext(amount_total)

    def baht_text(self, amount_total):
        if amount_total >= 100:
                amount_total_text = str(amount_total).split('.')

                amount_text_before_point = amount_total_text[0]
                amount_text_after_point = amount_total_text[1]
                before_point_ten = int(amount_text_before_point[len(amount_text_before_point) - 2])
                after_point = int(amount_text_after_point)
                if before_point_ten == 0:
                    amount_before_point = float(amount_text_before_point) - 1
                    amount_text_before_point = bahttext(amount_before_point)
                    baht_text = amount_text_before_point.split('บาทถ้วน')
                    if after_point != 0:
                        after_point = float(after_point) * 0.01
                        amount_text_after_point = bahttext(after_point).split('บาท')
                        baht_text = baht_text[0] + 'หนึ่งบาท' + amount_text_after_point[1]
                else:
                    baht_text = baht_text[0] + 'หนึ่งบาทถ้วน'

                    return baht_text
        else:
             baht_text = bahttext(amount_total)

        return baht_text

        return bahttext(amount_total)

    def num2_words(self, amount_total):
        before_point = ""
        amount_total_str = str(amount_total)
        for i in range(0,len(amount_total_str)):
            if amount_total_str[i] != ".":
                before_point += amount_total_str[i]
            else:
                break

        after_point = float(amount_total) - float(before_point)
        after_point = locale.format("%.2f", float(after_point), grouping=True)
        after_point = float(after_point)
        before_point = float(before_point)

        # print before_point
        # print after_point
        before_point_str = num2words(before_point)
        after_point_str = num2words(after_point)
        if after_point_str == 'zero':
            before_point_str += ' Only'
        else:
            for i in range(4,len(after_point_str)):
                before_point_str += after_point_str[i]

        n2w_origianl = before_point_str
        #print n2w_origianl
        # n2w_origianl = num2words(float(amount_total))
        n2w_new = ""
        for i in range(len(n2w_origianl)):
            if i == 0:
                n2w_new += n2w_origianl[i].upper()
            else:
                if n2w_origianl[i] != ",":
                    if n2w_origianl[i - 1] == " ":
                        n2w_new += n2w_origianl[i].upper()
                    else:
                        n2w_new += n2w_origianl[i]

        # print n2w_origianl
        # print n2w_new
        return n2w_new


class purchase_request_line(models.Model):
    _inherit = "purchase.request.line"


    # get total description line
    def get_line(self, data):
        return data.count("\n")








