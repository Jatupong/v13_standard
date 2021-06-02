# -*- coding: utf-8 -*-
from odoo import fields, api, models, _


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    numbe_text = fields.Char(String='Number Discount')

    @api.model_create_multi
    def create(self, vals_list):
        res = super(AccountMoveLine, self).create(vals_list)
        for obj in res:
            if obj.purchase_line_id:
                numbe_text = ''
                if obj.purchase_line_id.discount_ontop1:
                    numbe_text += str(obj.purchase_line_id.discount_ontop1) + '%'
                if obj.purchase_line_id.discount_ontop2:
                    numbe_text += str(obj.purchase_line_id.discount_ontop2) + '%'
                if obj.purchase_line_id.discount_ontop3:
                    numbe_text += str(obj.purchase_line_id.discount_ontop3) + '%'
                obj.update({'numbe_text': numbe_text
                            })

        return res
