# -*- coding: utf-8 -*-

from odoo import models, fields, api


class RequisitionLine(models.Model):
    _inherit = 'requisition.line'

    number = fields.Integer()


class MaterialPurchaseRequisition(models.Model):
    _inherit = 'material.purchase.requisition'

    is_number_line = fields.Boolean(compute='get_number', store=True, compute_sudo=True)

    @api.depends('requisition_line_ids')
    def get_number(self):
        for obj in self:
            number = 1
            for line in obj.requisition_line_ids.filtered(lambda x: x.product_id and x.id).sorted(lambda x: x.id):
                line.number = number
                number += 1
            obj.is_number_line = True