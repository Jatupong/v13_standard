# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    minimum_amount = fields.Float('Minimum Amount')
    maximum_amount = fields.Float('Maximum Amount')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        config_parameter = self.env['ir.config_parameter'].sudo()
        minimum_amount = (config_parameter.get_param('sale_approval.minimum_amount'))
        maximum_amount = (config_parameter.get_param('sale_approval.maximum_amount'))
        res.update(minimum_amount=float(minimum_amount))
        res.update(maximum_amount=float(maximum_amount))
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        config_parameter = self.env['ir.config_parameter'].sudo()
        config_parameter.set_param("sale_approval.minimum_amount", self.minimum_amount)
        config_parameter.set_param("sale_approval.maximum_amount", self.maximum_amount)


class SaleOrder(models.Model):
    _inherit = "sale.order"
     
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('demo', 'Demo Order'),
        ('waiting_for_approval', 'Waiting For Approval'),
        ('approved', 'Approved'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')
    approver_id = fields.Many2one('res.users', 'Sale Order Approver', readonly=True, copy=False, track_visibility='onchange', default=lambda self: self.env.user)
    discount_notes = fields.Float('Discount Note')
    next_discount_amount = fields.Float('Next Discount Amount')

    def action_approved(self):
        print('def action_approved')
        active_ids = self.env.context.get('active_ids', [])

        demo_approved = self.action_demo_approved()
        if not demo_approved:
            for sale_order in self:
                sale_order.check_discount_line()
                allow_amount_total = sale_order.check_amount_total()
                if not allow_amount_total:
                    if not active_ids:
                        raise UserError(_(
                            'Your approval limit is lesser then sale order total amount. Click on "Ask for Approval" for Higher value.'))
                    else:
                        raise UserError(
                            _('Your approval limit is lesser then sale order total amount. %s') % (sale_order.name))
                # if not sale_order.approver_id == self.env.user:
                #     raise UserError(_('You can not confirm this sale order. You have asked for Higher value.'))
                sale_order.write({'state':'approved'})

        return demo_approved

    # def action_confirm(self):
    #     print('def action_confirm')
    #     for sale_order in self:
    #         sale_order.check_discount_line()
    #         minimum_amount =0.00; maximum_amount =0.00
    #         if self.env['ir.config_parameter'].sudo().get_param('sale_approval.minimum_amount'):
    #             minimum_amount = float(self.env['ir.config_parameter'].sudo().get_param('sale_approval.minimum_amount'))
    #         if self.env['ir.config_parameter'].sudo().get_param('sale_approval.maximum_amount'):
    #             maximum_amount = float(self.env['ir.config_parameter'].sudo().get_param('sale_approval.maximum_amount'))
    #         if sale_order.amount_total >= minimum_amount and sale_order.amount_total <= maximum_amount:
    #             if not sale_order.amount_total <= sale_order.approver_id.sale_order_amount_limit:
    #                 raise UserError(_('Your approval limit is lesser then sale order total amount.Click on "Ask for Approval" for Higher value.'))
    #             if not sale_order.approver_id == self.env.user:
    #                 raise UserError(_('You can not confirm this sale order. You have asked for Higher value.'))
    #     return super(SaleOrder, self).action_confirm()
    
    def get_discount(self):
        return self.env.context.get('discount_percentage', 0)
    
    def get_reason_notes(self):
        return self.env.context.get('discount_notes', '')
    
    def escalate_order(self):
        self.ensure_one()
        template = self.env['ir.model.data'].get_object('sale_approval', 'email_template_sale_approval_mail')
        self.env['mail.template'].browse(template.id).send_mail(self.id,force_send=True)
        return True

    def get_requested_approve(self):
        body_message = ''
        check = False
        if self.env.context.get('is_for_amount', False):
            body_message += ' Amount'
            check = True
        if self.env.context.get('is_for_discount', False):
            if check:
                body_message += ','
            check = True
            body_message += ' Discount'
        if check:
            return body_message
        else:
            return False

    def action_quotation_send(self):
        for sale_order in self:
            sale_order.check_discount_line()
        return super(SaleOrder, self).action_quotation_send()

    def check_discount_line(self):
        # print('def check_discount_line')
        active_ids = self.env.context.get('active_ids', [])
        for line in self.order_line:
            # approver_id = self.approver_id
            approver_id = self.env.user
            discount = line.get_discount_line()
            if discount > 0.0:
                # print('line : ', line.product_id.default_code)
                # print('discount : ', line.discount)
                # print('sale_order_discount_limit : ', approver_id.sale_order_discount_limit)
                if not discount <= approver_id.sale_order_discount_limit:
                    if not active_ids:
                        raise UserError(_('Your discount limit is lesser than given discount.! Must ask to approve'))
                    else:
                        raise UserError(_('Your discount limit is lesser than given discount. %s') % (line.order_id.name))

    def check_amount_total(self):
        print('def check_amount_total')
        minimum_amount = 0.00
        maximum_amount = 0.00
        if self.env['ir.config_parameter'].sudo().get_param('sale_approval.minimum_amount'):
            minimum_amount = float(self.env['ir.config_parameter'].sudo().get_param('sale_approval.minimum_amount'))
        if self.env['ir.config_parameter'].sudo().get_param('sale_approval.maximum_amount'):
            maximum_amount = float(self.env['ir.config_parameter'].sudo().get_param('sale_approval.maximum_amount'))

        if self.amount_total >= minimum_amount and self.amount_total <= maximum_amount:
            # approver_id = sale_order.approver_id
            approver_id = self.env.user
            if not self.amount_total <= approver_id.sale_order_amount_limit:
                return False

        return True


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # @api.onchange('discount')
    # def onchang_discount_validate(self):
    #     if self.discount:
    #         approver_id = self.order_id.approver_id
    #         if not self.discount <= approver_id.sale_order_discount_limit:
    #             value = {
    #                 'discount': 00.0
    #             }
    #             warning = {
    #                 'title': _('Warning!'),
    #                 'message' : (_('Your discount limit is lesser than given discount.!'))
    #             }
    #             return {'warning': warning, 'value': value}

    def get_discount_line(self):
        ori_price = self.price_unit
        price_unit = self.price_unit
        price_unit = price_unit * (1 - (self.discount / 100.0))
        price_unit = price_unit * (1 - (self.discount_ontop1 / 100.0))
        price_unit = price_unit * (1 - (self.discount_ontop2 / 100.0))
        price_unit = price_unit * (1 - (self.discount_ontop3 / 100.0))
        if ori_price:
            discount = (ori_price - price_unit) * 100 / ori_price
        else:
            discount = (ori_price - price_unit) * 100 / 1
        discount = round(discount, 2)

        return discount


 

