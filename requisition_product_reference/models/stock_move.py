# -*- coding: utf-8 -*-

from odoo import models, fields ,api ,_
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp


class StockMove(models.Model):
    _inherit = "stock.move"

    requisition_qty = fields.Float('Requisition Qty', default=0.0, digits=dp.get_precision('Product Unit of Measure'))