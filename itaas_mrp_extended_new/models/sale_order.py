# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Book)

from odoo import fields, api, models, _
from bahttext import bahttext
from odoo.exceptions import UserError
from datetime import datetime, date

class sale_order(models.Model):
    _inherit = 'sale.order'

    manufacturing_ids = fields.One2many('mrp.production','sale_order_id',string='MO')
    count_mo = fields.Integer(string='Count MO',compute='get_compute_mo_to_sale',store=True)

    @api.depends('manufacturing_ids')
    def get_compute_mo_to_sale(self):
        for order in self:
            order.count_mo = len(order.manufacturing_ids)


    def action_view_mo(self):
        manufacturing_ids = self.mapped('manufacturing_ids')
        action = self.env.ref('mrp.mrp_production_action').read()[0]
        if len(manufacturing_ids) > 1:
            action['domain'] = [('id', 'in', manufacturing_ids.ids)]
        elif len(manufacturing_ids) == 1:
            form_view = [(self.env.ref('mrp.mrp_production_form_view').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = manufacturing_ids.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        # context = {
        #     'default_type': 'out_invoice',
        # }
        # if len(self) == 1:
        #     context.update({
        #         'default_partner_id': self.partner_id.id,
        #         'default_partner_shipping_id': self.partner_shipping_id.id,
        #         'default_invoice_payment_term_id': self.payment_term_id.id or self.partner_id.property_payment_term_id.id or self.env['account.move'].default_get(['invoice_payment_term_id']).get('invoice_payment_term_id'),
        #         'default_invoice_origin': self.mapped('name'),
        #         'default_user_id': self.user_id.id,
        #     })
        # action['context'] = context
        return action


