# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Book)

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PurchaseRequestLineMakePurchaseOrder(models.TransientModel):
    _inherit = "purchase.request.line.make.purchase.order"

    department_id = fields.Many2one("hr.department", "Department",)

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
        department_ids = request_lines.mapped("request_id").mapped("department_id").ids
        if department_ids:
            res["department_id"] = department_ids[0]

        return res

    @api.model
    def _prepare_purchase_order_line(self, po, item):
        res = super(PurchaseRequestLineMakePurchaseOrder, self)._prepare_purchase_order_line(po, item)
        res.update({'department_id': item.line_id.department_id.id ,})

        return res

    @api.model
    def _get_order_line_search_domain(self, order, item):
        order_line_data = super(PurchaseRequestLineMakePurchaseOrder, self)._get_order_line_search_domain(order, item)
        if item.line_id.department_id:
            order_line_data.append(("department_id", "=", item.line_id.department_id.id))

        return order_line_data