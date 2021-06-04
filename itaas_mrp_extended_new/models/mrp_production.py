# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Book)

from odoo import fields, api, models, _
from bahttext import bahttext
from odoo.exceptions import UserError
from datetime import datetime, date

class mrp_production(models.Model):
    _inherit = 'mrp.production'

    sale_order_id = fields.Many2one('sale.order',string='Sale Order',compute='get_so',store=True)
    product_parent_fg_id = fields.Many2one('product.product',compute="get_so", store=True, readonly=True, copy=False)
    requisition_ids = fields.One2many('material.purchase.requisition','production_id',string='Requisition')
    requisition_count = fields.Integer(string='Requisition Count',compute='get_requisition_count')

    @api.depends('requisition_ids')
    def get_requisition_count(self):
        for mo in self:
            mo.requisition_count = len(mo.requisition_ids)

    @api.depends('origin','procurement_group_id')
    def get_so(self):
        for mo in self:
            so_id = False
            production_id = False
            print (mo.origin)
            if mo.origin:
                so_id = self.env['sale.order'].search([('name','=',mo.origin)],limit=1)
            if not so_id and mo.origin:
                production_id = self.env['mrp.production'].search([('name','=',mo.origin)],limit=1)

            if so_id:
                mo.sale_order_id = so_id

            if production_id:
                mo.product_parent_fg_id = production_id.product_id


    def material_request(self):
        requisition_obj = self.env['material.purchase.requisition']
        employee_id = self.env.user.employee_id
        internal_picking_id = requisition_obj._default_picking_internal_type()
        if not employee_id:
            raise UserError(_('สร้างรายชื่อพนักงานที่เกี่ยวกับผู้ใช้คนนี้'))
        if not internal_picking_id:
            raise UserError(_('ตรวจสอบ Default Picking สำหรับการเบิก'))

        val = {
            'employee_id': employee_id.id,
            'department_id': employee_id.department_id.id,
            'reason_for_requisition': 'Production:' + str(self.name),
            'source_location_id':internal_picking_id.default_location_src_id.id,
            'destination_location_id': internal_picking_id.default_location_dest_id.id,
            'production_id': self.id,
        }
        requisition_id = requisition_obj.create(val)
        print (requisition_id)
        requisition_id.with_context(doc='mo').action_product_reference()


    def action_view_requisition(self):
        requisition_ids = self.mapped('requisition_ids')
        action = self.env.ref('bi_material_purchase_requisitions.action_material_purchase_requisition').read()[0]
        if len(requisition_ids) > 1:
            action['domain'] = [('id', 'in', requisition_ids.ids)]
        elif len(requisition_ids) == 1:
            form_view = [(self.env.ref('bi_material_purchase_requisitions.material_purchase_requisition_form_view').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = requisition_ids.id
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





