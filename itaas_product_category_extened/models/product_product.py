# -*- coding: utf-8 -*-
# Copyright (C) 2016-2017  ITtaas.
from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from dateutil.rrule import (YEARLY,MONTHLY,WEEKLY,DAILY)
from datetime import datetime, timedelta, date
from pytz import timezone
import pytz
import calendar

import uuid

from datetime import datetime, timedelta


class product_product(models.Model):
    _inherit = "product.product"

    main_categ_id = fields.Many2one('product.category', string='Main Category',compute='get_main_category',store=True)

    @api.depends('categ_id','categ_id.parent_id')
    def get_main_category(self):
        for product in self:
            if product.categ_id:
                if product.categ_id.parent_id:
                    product.main_categ_id = product.categ_id.parent_id
                else:
                    product.main_categ_id = product.categ_id












