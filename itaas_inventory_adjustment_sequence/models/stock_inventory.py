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

strptime = datetime.strptime
strftime = datetime.strftime


class stock_inventory(models.Model):
    _inherit = "stock.inventory"

    number = fields.Char(string='Number')

    def action_start(self):
        if not self.number:
            self.number = self.env['ir.sequence'].next_by_code('inv.adjust.sequence')
        return super(stock_inventory, self).action_start()