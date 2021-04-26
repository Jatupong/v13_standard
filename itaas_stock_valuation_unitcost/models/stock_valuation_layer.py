# -*- coding: utf-8 -*-
# Copyright (C) 2019-present  Technaureus Info Solutions(<http://www.technaureus.com/>).

from odoo import models, fields, api
from openerp import api, fields, models, _
from openerp.osv import expression
from openerp.tools import float_is_zero
from openerp.tools import float_compare, float_round
from openerp.tools.misc import formatLang
from openerp.exceptions import UserError, ValidationError
from datetime import datetime, date


import time
import math


class stock_valuation_layer(models.Model):
    _inherit = "stock.valuation.layer"

    def update_unit_cost(self):
        for valuation in self:
            valuation.value = valuation.unit_cost * valuation.quantity
            valuation.remaining_value = valuation.unit_cost * valuation.remaining_qty


