# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Book)

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    combine_order_id = fields.Many2one('sale.order', string='Combine Order')

    def action_combine_order(self):
        active_ids = self.env.context.get('active_ids', [])
        sale_order = self.env['sale.order'].browse(active_ids).filtered(lambda x: x.state in ['draft','sent','approved'])
        partner_ids = sale_order.mapped('partner_id')
        if len(sale_order) > 1 and len(partner_ids) == 1:
            context = dict(self.env.context or {})
            sale_order_qt = sale_order.filtered(lambda x: x.state in ['draft', 'sent'])
            if sale_order_qt:
                sale_order_qt.action_approved()
            wizard_form_id = self.env.ref('itaas_quotation_combine_order.view_quotation_combine_wizard').id
            return {'type': 'ir.actions.act_window',
                    'res_model': 'quotation.combine.wizard',
                    'view_mode': 'form',
                    'views': [(wizard_form_id, 'form')],
                    'context': context,
                    'target': 'new'}
        else:
            raise UserError(_('Please check customer or state.'))