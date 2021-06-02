# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today  itaas.co.th

from bahttext import bahttext
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime,timedelta,date
from dateutil.relativedelta import relativedelta
import locale
import time
from odoo import api,fields, models
from odoo.osv import osv
# from odoo.report import report_sxw
from odoo.tools import float_compare, float_is_zero


class AccountMoveLine(models.Model):
    _inherit ="account.move.line"

    def _get_computed_name(self):
        self.ensure_one()
        super(AccountMoveLine, self)._get_computed_name()
        if not self.product_id:
            return ''

        if self.partner_id.lang:
            product = self.product_id.with_context(lang=self.partner_id.lang)
        else:
            product = self.product_id

        values = []
        if product.name:
            values.append(product._get_partner_ref())
            # print('values : ',values)
        if self.journal_id.type == 'sale':
            if product.description_sale:
                values.append(product.description_sale)
        elif self.journal_id.type == 'purchase':
            if product.description_purchase:
                values.append(product.description_purchase)
        return '\n'.join(values)