# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.tools.float_utils import float_is_zero


class Account_move_inherit(models.Model):
    _inherit = 'account.move'


    bill_to_id = fields.Many2one('res.partner', string='Bill to')

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        print('========================')
        self.bill_to_id = self.partner_id.bill_to_id


    # def action_move_create(self):
    #     print ('update bill to')
    #     result = super(Account_move_inherit, self).action_move_create()
    #     for inv in self:
    #         if  inv.bill_to_id:
    #             ###########find move line same with account_id that mean it is account receiabale change to bill to
    #             move_line_account_id = inv.line_ids.filtered(lambda ml: ml.account_id == inv.account_id)
    #             if move_line_account_id:
    #                 ############# Update partner id of ar to bill to but the rest still be normal partner field
    #                 move_line_account_id.update({'partner_id': inv.bill_to_id.id})
    #
    #     return result





