# -*- coding: utf-8 -*-

from odoo import models, fields ,api ,_
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    # update consu
    # def button_mark_done(self):
    #
    #     for move in self.move_raw_ids:
    #         if move.requisition_qty > move.product_qty:
    #             move.update({'quantity_done': move.requisition_qty})
    #
    #     return super(MrpProduction, self).button_mark_done()