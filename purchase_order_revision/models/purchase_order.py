# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Book)

from odoo import fields, api, models, _
from bahttext import bahttext
from odoo.exceptions import UserError
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    current_revision_id = fields.Many2one('purchase.order', string='Current revision', readonly=True,copy=True)
    old_revision_ids = fields.One2many('purchase.order', 'current_revision_id', string='Old revisions', readonly=True,
                                       context={'active_test': False})
    revision_number = fields.Integer(string='Revision',copy=False,default=0)
    unrevisioned_name = fields.Char(string='Original Order Reference',copy=True,readonly=True)
    active = fields.Boolean(default=True)
    has_old_revisions = fields.Boolean()

    _sql_constraints = [
        ('revision_unique',
         'unique(unrevisioned_name, revision_number, company_id)',
         'Order Reference and revision must be unique per Company.'),
    ]

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        if default is None:
            default = {}
            default['unrevisioned_name'] = False

        return super(PurchaseOrder, self).copy(default=default)

    def copy_revision_with_context(self):
        default_data = self.default_get([])
        new_rev_number = self.revision_number + 1

        default_data .update({
            'revision_number': new_rev_number,
            'unrevisioned_name': self.unrevisioned_name,
            'name': '%s-%02d' % (self.unrevisioned_name, new_rev_number),
            'old_revision_ids': [(4, self.id, False)],
            'has_old_revisions':True,
        })
        new_revision = self.copy(default_data)
        self.old_revision_ids.write({
            'current_revision_id': new_revision.id,
        })
        self.write({'active': False,
                    'state': 'cancel',
                    'current_revision_id': new_revision.id,
                    })

        return new_revision

    @api.model
    def create(self, values):
        res = super(PurchaseOrder, self).create(values)
        if not res.unrevisioned_name:
            res.unrevisioned_name = res.name

        return res

    def create_revision(self):
        revision_ids = []
        # Looping over purchase order records
        for purchase_order_rec in self:
            # Calling  Copy method
            copied_purchase_rec = purchase_order_rec.copy_revision_with_context()

            msg = _('New revision created: %s') % copied_purchase_rec.name
            copied_purchase_rec.message_post(body=msg)
            purchase_order_rec.message_post(body=msg)

            revision_ids.append(copied_purchase_rec.id)

        action = {
            'type': 'ir.actions.act_window',
            'name': _('New Purchases Order Revisions'),
            'res_model': 'purchase.order',
            'domain': "[('id', 'in', %s)]" % revision_ids,
            'auto_search': True,
            'views': [
                (self.env.ref('purchase.purchase_order_tree').id, 'tree'),
                (self.env.ref('purchase.purchase_order_form').id, 'form')],
            'target': 'current',
            'nodestroy': True,
        }

        # Returning the new purchase order view with new record.
        return action
