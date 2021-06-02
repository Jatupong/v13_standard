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


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _get_product_purchase_description(self, product_lang):
        self.ensure_one()
        super(PurchaseOrderLine, self)._get_product_purchase_description(product_lang)
        name = product_lang._get_partner_ref()
        if product_lang.description_purchase:
            name += '\n' + product_lang.description_purchase

        return name