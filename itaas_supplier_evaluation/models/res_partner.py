# -*- coding: utf-8 -*-
# Copyright (C) 2020-today  ITAAS

from datetime import datetime, timedelta, date
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    evaluation_ids = fields.One2many('stock.evaluation', 'partner_id', string='Evaluation', copy=False, auto_join=True)
