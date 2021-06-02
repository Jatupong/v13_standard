# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json

from odoo import models, fields, api, _
from odoo.exceptions import UserError



class SaleOrder(models.Model):
    _inherit = 'sale.order'



    def _create_delivery_line(self, carrier, price_unit):
        if not price_unit:
            return False

        return super(SaleOrder, self)._create_delivery_line(carrier, price_unit)