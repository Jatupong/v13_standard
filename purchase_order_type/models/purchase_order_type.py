# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Book)

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PurchaseOrderTyp(models.Model):
    _name = 'purchase.order.type'
    _description = 'Type of purchase order'

    @api.model
    def _get_default_sequence_id(self):
        seq_type = self.env.ref('purchase.seq_purchase_order')
        return seq_type

    name = fields.Char(string='Name', required=True, translate=True)
    active = fields.Boolean('Active', default=True, track_visibility='onchange')
    description = fields.Text(string='Description', translate=True)
    sequence_id = fields.Many2one('ir.sequence', string='Entry Sequence', copy=False, default=_get_default_sequence_id)
    # journal_id = fields.Many2one('account.journal', string='Billing Journal', domain=[('type', '=', 'purchase')])
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    payment_term_id = fields.Many2one('account.payment.term', 'Payment Term')
    incoterm_id = fields.Many2one('account.incoterms', 'Incoterm')
    picking_type_id = fields.Many2one('stock.picking.type', 'Deliver To', domain=[('code', '=', 'incoming')])
