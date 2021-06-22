# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Book)

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PurchaseRequestLineMakePurchaseOrder(models.TransientModel):
    _inherit = "purchase.request.line.make.purchase.order"

    purchase_type_id = fields.Many2one('purchase.order.type', string='Purchase Type')

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        active_model = self.env.context.get("active_model", False)
        request_line_ids = []
        if active_model == "purchase.request.line":
            request_line_ids += self.env.context.get("active_ids", [])
        elif active_model == "purchase.request":
            request_ids = self.env.context.get("active_ids", False)
            request_line_ids += (self.env[active_model].browse(request_ids).mapped("line_ids.id"))
        if not request_line_ids:
            return res
        request_lines = self.env["purchase.request.line"].browse(request_line_ids)
        purchase_type_ids = request_lines.mapped("request_id").mapped("purchase_type_id").ids
        if purchase_type_ids:
            res["purchase_type_id"] = purchase_type_ids[0]

        return res

    def make_purchase_order(self):
        if self.purchase_order_id:
            if self.purchase_order_id.type_id:
                if self.purchase_order_id.type_id != self.purchase_type_id:
                    raise UserError(_("The purchase has purchase order type not same."))
        return super(PurchaseRequestLineMakePurchaseOrder, self).make_purchase_order()

    @api.model
    def _prepare_purchase_order(self, picking_type, group_id, company, origin):
        data = super(PurchaseRequestLineMakePurchaseOrder, self)._prepare_purchase_order(picking_type, group_id, company, origin)
        if self.purchase_type_id:
            data.update({"type_id": self.purchase_type_id.id,})

        return data