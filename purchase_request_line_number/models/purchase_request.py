# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PurchaseRequestLine(models.Model):
    _inherit = 'purchase.request.line'

    number = fields.Integer()


class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    is_number_line = fields.Boolean(compute='get_number', store=True, compute_sudo=True)

    @api.depends('line_ids')
    def get_number(self):
        for obj in self:
            line_ids = obj.line_ids.filtered(lambda x: x.id).sorted(lambda x: x.id)
            # print('line_ids : ',line_ids)
            number = 1
            for line in line_ids:
                line.number = number
                number += 1
            obj.is_number_line = True