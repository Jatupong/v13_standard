# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class PickingMultiAssignDone(models.TransientModel):
    _name = "picking.multi.assign.qty"
    _description = "Stock Picking Assign Done QTY"

    def assign_done_qty(self):
        stock_picking_ids = self.env['stock.picking'].browse(self._context.get('active_ids', []))

        for picking in stock_picking_ids.filtered(lambda x: x.state in ('assigned','confirmed')):
            picking.assign_done_qty()
        return {'type': 'ir.actions.act_window_close'}

