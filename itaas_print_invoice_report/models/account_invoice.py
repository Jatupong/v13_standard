# -*- coding: utf-8 -*-

from odoo import fields, api, models, _
from bahttext import bahttext
from num2words import num2words
import locale

class AccountInvoice_inherit(models.Model):
    _inherit ="account.move"


    def baht_text(self, amount_total):
        return bahttext(amount_total)

    def num2_words(self, amount_total):
        before_point = ""
        amount_total_str = str(amount_total)
        for i in range(0, len(amount_total_str)):
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
            for i in range(4, len(after_point_str)):
                before_point_str += after_point_str[i]

        n2w_origianl = before_point_str
        # print n2w_origianl
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

    def get_origin(self,invoice_origin):
        print(invoice_origin)
        if invoice_origin:
            account = self.search([('name', '=', invoice_origin)])
            return account.amount_untaxed

        else:
            account = 0.0
            return account


    # @api.multi
    # def invoice_print(self):
    #     """ Print the invoice and mark it as sent, so that we can see more
    #         easily the next step of the workflow
    #     """
    #     self.ensure_one()
    #     self.sent = True
    #     if self.user_has_groups('account.group_account_invoice'):
    #         return self.env.ref('itaas_print_invoice_report.invoice_report').report_action(self)
    #     else:
    #         return self.env.ref('itaas_print_invoice_report.invoice_report').report_action(self)

    # @api.multi
    # def action_invoice_sent(self):
    #     """ Open a window to compose an email, with the edi invoice template
    #         message loaded by default
    #     """
    #     self.ensure_one()
    #     template = self.env.ref('itaas_print_invoice_report.new_final_email_template_edi_invoice', False)
    #     compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
    #     ctx = dict(
    #         default_model='account.move',
    #         default_res_id=self.id,
    #         default_use_template=bool(template),
    #         default_template_id=template and template.id or False,
    #         default_composition_mode='comment',
    #         mark_invoice_as_sent=True,
    #         custom_layout="account.mail_template_data_notification_email_account_invoice",
    #         force_email=True
    #     )
    #     return {
    #         'name': _('Compose Email'),
    #         'type': 'ir.actions.act_window',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_model': 'mail.compose.message',
    #         'views': [(compose_form.id, 'form')],
    #         'view_id': compose_form.id,
    #         'target': 'new',
    #         'context': ctx,
    #     }

    def get_line(self, data, max_line):
        # this function will count number of \n
        line_count = data.count("\n")
        if not line_count:
            # print "line 0 - no new line or only one line"
            # lenght the same with line max
            if not len(data) % max_line:
                line_count = len(data) / max_line
            # lenght not the same with line max
            # if less than line max then will be 0 + 1
            # if more than one, example 2 line then will be 1 + 1
            else:
                line_count = len(data) / max_line + 1
        elif line_count:
            # print "line not 0 - has new line"
            # print line_count
            # if have line count mean has \n then will be add 1 due to the last row have not been count \n
            line_count += 1
            data_line_s = data.split('\n')
            for x in range(0, len(data_line_s), 1):
                # print data_line_s[x]
                if len(data_line_s[x]) > max_line:
                    # print "more than one line"
                    line_count += len(data_line_s[x]) / max_line
        if line_count > 1:
            ##############if more then one line, it is new line not new row, so hight will be 80%
            line_count = line_count * 0.8
        return line_count

    def get_break_line(self, max_body_height, new_line_height, row_line_height, max_line_lenght):
        break_page_line = []
        count_height = 0
        count = 1
        for line in self.invoice_line_ids:
            line_name = self.get_lines(line.name, max_line_lenght)
            # remove by row height to line
            # line_height = row_line_height + ((self.get_line(line.name, max_line_lenght)) * new_line_height)
            line_height = row_line_height * line_name
            count_height += line_height
            if count_height > max_body_height:
                break_page_line.append(count - 1)
                count_height = line_height
            count += 1
        # last page
        break_page_line.append(count - 1)

        print(break_page_line)
        return break_page_line

    def get_break_line_invoice(self, max_body_height, new_line_height, row_line_height, max_line_lenght):
        break_page_line = []
        count_height = 0
        count = 1
        # print 'get_break_line_invoice'
        for line in self.invoice_line_ids:
            # print line.product_id
            # print line.product_id.default_code
            # default_code

            # print count
            line_height = row_line_height + ((self.get_line(line.name, max_line_lenght)) * new_line_height)
            count_height += line_height
            if count_height > max_body_height:
                break_page_line.append(count - 1)
                count_height = line_height
            count += 1
        # last page
        break_page_line.append(count - 1)
        # print "break_page_line"
        # print break_page_line
        return break_page_line


