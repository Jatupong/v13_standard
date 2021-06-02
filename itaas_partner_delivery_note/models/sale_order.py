# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Book)


from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    note_for_delivery = fields.Text(string='Note for Delivery')

    @api.onchange('partner_shipping_id', 'partner_id')
    def onchange_partner_shipping_id(self):
        super(SaleOrder, self).onchange_partner_shipping_id()
        if self.partner_shipping_id:
            self.note_for_delivery = self.partner_id.note_for_delivery
        elif self.partner_id:
            self.note_for_delivery = self.partner_id.note_for_delivery
        else:
            return

    @api.model
    def create(self, vals):
        if self._context.get('default_order_type') and self._context.get('default_order_type') == 'sale':
            if 'partner_id' in vals:
                partner = self.env['res.partner'].browse(vals.get('partner_id'))
                vals.update({'note_for_delivery':partner.note_for_delivery or ''})

        return super(SaleOrder, self).create(vals)