# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class SaleApprovalReason(models.TransientModel):
    _name = 'sale.approval.reason'

    # approval_for = fields.Selection([
    # ('for_amount', 'Request For Amount'),
    # ('for_discount', 'Request For Discount'),
    # ], 'Approve Type', copy=False, required=True, select=True)
    is_for_amount = fields.Boolean('Request For Amount', copy=False)
    is_for_discount = fields.Boolean('Request For Discount', copy=False)
    requested_discount = fields.Float('Requested Discount')
    notes = fields.Text('Notes')
    sale_id = fields.Many2one('sale.order')
    approver_id = fields.Many2one('res.users', 'Sale Order Approver')

    @api.model
    def default_get(self, fields):
        if len(self.env.context.get('active_ids', list())) > 1:
            raise UserError(_("You may only request one order at a time."))
        res = super(SaleApprovalReason, self).default_get(fields)
        if self.env.context.get('active_id') and self.env.context.get('active_model') == 'sale.order':
            sale = self.env['sale.order'].browse(self.env.context.get('active_id'))
            if sale.exists():
                is_for_discount = self.check_discount_line(sale)
                allow_amount_total = sale.check_amount_total()
                if not allow_amount_total:
                    is_for_amount = True
                else:
                    is_for_amount = False

                res.update({'sale_id': sale.id,
                            'is_for_amount': is_for_amount,
                            'is_for_discount': is_for_discount,})
        return res

    @api.onchange('is_for_amount','is_for_discount')
    def onchange_allow_approver(self):
        sale = self.env['sale.order'].browse(self.env.context.get('active_id'))
        # print('onchange_allow_approver sale : ',sale)
        domain = []
        if self.is_for_amount or self.is_for_discount:
            domain.append(('sale_order_can_approve', '=', 'yes'))
            if self.is_for_amount:
                domain.append(('sale_order_amount_limit', '>=', sale.amount_total))
            if self.is_for_discount:
                requested_discount = max(self.sale_id.order_line.mapped('discount'))
                domain.append(('sale_order_discount_limit', '>=', requested_discount))
        approver_ids = self.env['res.users'].search(domain)
        if approver_ids:
            self.approver_id = approver_ids[0].id

        return {'domain': {'approver_id': [('id', 'in', approver_ids.ids)]}}


    def check_discount_line(self ,sale):
        for line in sale.order_line:
            discount = line.get_discount_line()
            if discount:
                if not discount <= sale.env.user.sale_order_discount_limit:
                    return True
        return False

    def approve(self):
        sale_br_obj = self.env['sale.order'].browse(self._context.get('active_ids'))[0]
        user_obj = self.env['res.users']
        approver_id = self.approver_id
        requested_discount = False

        if self.is_for_amount:
            user_search_amount = user_obj.search([('sale_order_amount_limit', '>=', sale_br_obj.amount_total),
                                                  ('id', '=',approver_id.id),
                                                  ('sale_order_can_approve', '=', 'yes')],
                                                 limit=1, order='sale_order_amount_limit')
            if user_search_amount:
                approver_id = user_search_amount.id
            else:
                raise UserError('Approver is not set for this Amount Limit. Please allocate approver')

        # if self.approval_for == 'for_discount':
        #     if self.requested_discount:
        #         user_search_discount = user_obj.search([('sale_order_discount_limit', '>=', self.requested_discount)], order='sale_order_discount_limit')
        #         if user_search_discount:
        #             discount_approver_user_id = user_search_discount[0]
        #         else:
        #             raise UserError('Approver is not set for this Amount Limit. Please allocate approver')
        #         sale_br_obj.write({'approver_id': discount_approver_user_id.id, 'next_discount_amount': self.requested_discount, 'state': 'waiting_for_approval'})

        if self.is_for_discount:
            requested_discount = max(self.sale_id.order_line.mapped('discount'))
            user_search_discount = user_obj.search([('sale_order_discount_limit', '>=', requested_discount),
                                                    ('id', '=', approver_id.id),
                                                    ('sale_order_can_approve', '=', 'yes')],
                                                   limit=1, order='sale_order_discount_limit')
            if user_search_discount:
                approver_id = user_search_discount.id
            else:
                raise UserError('Approver is not set for this Discount Limit. Please allocate approver')

        if self.is_for_discount or self.is_for_amount:
            sale_br_obj.write({'approver_id': approver_id,
                               'next_discount_amount': requested_discount,
                               'state': 'waiting_for_approval'})

        ctx = self.env.context.copy()
        ctx.update({'discount_percentage': float(requested_discount),
                    'discount_notes': str(self.notes),
                    'is_for_discount': self.is_for_discount,
                    'is_for_amount': self.is_for_amount
                    })
        sale_br_obj.with_context(ctx).escalate_order()

        return True