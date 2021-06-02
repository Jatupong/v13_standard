# -*- coding: utf-8 -*-
# Copyright (C) 2019-Today  Technaureus Info Solutions Pvt. Ltd.(<http://technaureus.com/>).
from odoo.exceptions import UserError

from odoo import api, fields, models,_


class Purchase_request(models.Model):
    _inherit = "material.purchase.requisition"

    type_request_id = fields.Many2one('type.request',string='Type Request')

    def action_approve(self):
        if self.type_request_id:
            user = self.env.uid
            print('user:',user)
            user_approve = self.type_request_id.users_ids.filtered(lambda x: x.id == user)
            print('user_approve:',user_approve)
            if user_approve:
                self.create_picking_po()
            else:
                raise UserError(_("Can't Approve Please Check Type Request"))


class Type_Request(models.Model):
    _name = "type.request"
    _rec_name = 'name'


    name = fields.Char('Name')
    users_ids = fields.Many2many('res.users',string='Approve')


