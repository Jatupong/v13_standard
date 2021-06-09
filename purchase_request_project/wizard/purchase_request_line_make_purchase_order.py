# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Book)

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PurchaseRequestLineMakePurchaseOrder(models.TransientModel):
    _inherit = "purchase.request.line.make.purchase.order"

    @api.model
    def _prepare_item(self, line):
        res = super()._prepare_item(line)
        # print('res : ',res)
        if line.project_id:
            res.update({'project_id':line.project_id.id})

        return res

    @api.model
    def _prepare_purchase_order_line(self, po, item):
        res = super(PurchaseRequestLineMakePurchaseOrder, self)._prepare_purchase_order_line(po, item)
        res.update({'project_id': item.line_id.project_id.id ,})

        return res

    @api.model
    def _get_order_line_search_domain(self, order, item):
        order_line_data = super(PurchaseRequestLineMakePurchaseOrder, self)._get_order_line_search_domain(order, item)
        if item.line_id.project_id:
            order_line_data.append(("project_id", "=", item.line_id.project_id.id))

        return order_line_data


class PurchaseRequestLineMakePurchaseOrderItem(models.TransientModel):
    _inherit = "purchase.request.line.make.purchase.order.item"

    project_id = fields.Many2one("project.project", "Project",)