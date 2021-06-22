# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Book)

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def _get_order_type(self):
        user_id = self.env['res.users'].browse(self.env.uid)

        return user_id.purchase_type

    type_id = fields.Many2one('purchase.order.type', string='Purchase Type', default=_get_order_type)

    @api.model
    def create(self, vals):
        if (vals.get('name', 'New') == 'New' or 'name' not in vals) and 'type_id' in vals:
            purchase_type = self.env['purchase.order.type'].browse(vals['type_id'])
            if purchase_type.sequence_id:
                vals['name'] = purchase_type.sequence_id.next_by_id()
            else:
                raise UserError(_("The purchase order type hasn't entry sequence."))
        return super(PurchaseOrder, self).create(vals)

    @api.onchange('type_id')
    def onchange_type_id(self):
        for order in self:
            if order.type_id.payment_term_id:
                order.payment_term_id = order.type_id.payment_term_id.id or False
            if order.type_id.incoterm_id:
                order.incoterm_id = order.type_id.incoterm_id.id or False
            if order.type_id.picking_type_id:
                order.picking_type_id = order.type_id.picking_type_id.id or False


class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    @api.model
    def _get_purchase_order_type(self):
        user_id = self.env['res.users'].browse(self.env.uid)

        return user_id.purchase_type

    purchase_type_id = fields.Many2one('purchase.order.type', string='Purchase Type', default=_get_purchase_order_type)

