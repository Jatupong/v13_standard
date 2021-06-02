# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################
from odoo.exceptions import UserError
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import date
from dateutil.relativedelta import relativedelta
import math



class SaleOrder(models.Model):
    _inherit = "sale.order"

    def roundup(self, x):
        return int(math.ceil(x / 10.0)) * 10

    def create_sale_quotation(self):
        if not self.order_line:
            raise ValidationError(_('''Please add some Order Lines'''))
        data = []
        for line in self.order_line:
            data.append((0, 0, {'sale_line_id': line.id}))
        if data:
            create_quote_id = self.env['create.sale.quotation'].create({'line_ids': data})
            if create_quote_id:
                action = self.env.ref('itaas_blanket_sale_order.action_create_sale_quotation').read()[0]
                action.update({'res_id': create_quote_id.id})
                return action

    @api.model
    def create(self, vals):
        if self._context.get('default_order_type') == 'blanket':
            vals['name'] = self.env['ir.sequence'].next_by_code('sale.blanket') or '/'
        return super(SaleOrder, self).create(vals)

    def open_blanket_order(self):
        self.blanket_state = 'open'

    def cancel_blanket_order(self):
        self.blanket_state = 'cancelled'

    def set_to_new_blanket_order(self):
        self.blanket_state = 'draft'

    def compute_sale_quote_count(self):
        for rec in self:
            rec.sale_quote_count = len(rec.blanket_order_ids.filtered(lambda x: x.state != 'cancel'))

    def view_sale_quotations(self):
        orders = self.mapped('blanket_order_ids')
        action = self.env.ref('sale.action_orders').read()[0]
        if len(orders) > 1:
            action['domain'] = [('id', 'in', orders.ids)]
        elif len(orders) == 1:
            action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
            action['res_id'] = orders.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def create_auto_all(self):
        max_time = 1
        for blanket_order in self:
            for line in blanket_order.order_line:
                if line.standard_qty:
                    line_max_time = line.product_uom_qty / line.standard_qty
                    if line_max_time > max_time:
                        max_time = line_max_time
                else:
                    raise UserError(_("Please assign standard qty for each line"))
        print (max_time)
        max_time = self.roundup(max_time)
        print (max_time)
        for i in range(0,int(max_time),1):
            self.create_auto_order_from_blanket_orders()

    def create_auto_order_from_blanket_orders(self):
        for blanket_order in self:
            consumed_qty_dict = {}
            new_quotations = []
            data = []
            for line in blanket_order.order_line:
                print ('REMAIN QTY')
                line.compute_consume_qty()
                line.compute_remaining_qty()
                print (line.remaining_qty)
                if line.remaining_qty <= 0:
                    continue
                data.append((0, 0, {'product_id': line.product_id.id,
                                    'product_uom': line.product_uom.id,
                                    'product_uom_qty': line.standard_qty,
                                    'price_unit': line.price_unit,
                                    'name': line.name,
                                    }))


                if line.next_date:
                    validity_date = line.next_date
                    delivery_date = line.next_delivery_date

                else:
                    validity_date = blanket_order.start_date
                    delivery_date = blanket_order.start_delivery_date

            if data:
                order_val = {
                    'partner_id': blanket_order.partner_id.id,
                    'date_order': validity_date,
                    'validity_date': blanket_order.blanket_expiry_date,
                    'commitment_date': delivery_date,
                    'order_line': data,
                }
                quotation_id = self.env['sale.order'].with_context(default_order_type='sale').create(order_val)
                if quotation_id:
                    new_quotations.append(quotation_id.id)

            for quote in new_quotations:
                blanket_order.blanket_order_ids = [(4, quote)]

            for line in blanket_order.order_line:
                line.update_next_date()  # update next_date (next_order_date=expiry_date) and next_delivery_date(commitment_date)

    def expire_blanket_orders(self):
        blanket_ids = self.env['sale.order'].search([('blanket_expiry_date', '=', date.today()),
                                                     ('order_type', '=', 'blanket')])
        if blanket_ids:
            for blanket_id in blanket_ids:
                blanket_id.blanket_state = 'expired'

    blanket_state = fields.Selection(selection=[('draft', 'New'),
                                                ('open', 'Open'),
                                                ('expired', 'Expired'),
                                                ('cancelled', 'Cancelled')], string='Blanket State', default='draft', copy=False)
    order_type = fields.Selection(selection=[('sale', 'Sale'), ('blanket', 'Blanket')], string='Type of Order')
    start_date = fields.Date(string='Start Order Date')
    start_delivery_date = fields.Date(string='Start Delivery Date')
    standard_frequency = fields.Integer(string='ความถี่ในการส่ง')
    blanket_expiry_date = fields.Date(string='Expiry Date')
    blanket_order_ids = fields.Many2many(comodel_name='sale.order', relation='sale', column1='order_type', column2='blanket_expiry_date', string='Blanket Quotation',copy=False)
    sale_quote_count = fields.Integer(string='Sale Orders', compute='compute_sale_quote_count')


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"



    def update_next_date(self):
        for record in self:
            if not record.next_date:
                record.next_date = record.order_id.start_date
                record.next_delivery_date = record.order_id.start_delivery_date
                record.period = record.order_id.standard_frequency

            record.next_date = record.next_date + relativedelta(days=record.period)
            record.next_delivery_date = record.next_delivery_date + relativedelta(days=record.period)

    def compute_remaining_qty(self):
        for record in self:
            record.remaining_qty = record.product_uom_qty - record.consumed_qty

    def compute_consume_qty(self):

        for order_line in self:
            consume_qty = 0
            # print ('---------------------------------------------------')
            for sale_order in order_line.order_id.blanket_order_ids.filtered(lambda x: x.state != 'cancel'):
                # print ('--SALE ORDER')
                # print (sale_order.name)
                # print (order_line.product_id)
                product_order_line_ids = sale_order.order_line.filtered(lambda x: x.product_id == order_line.product_id)
                # print(product_order_line_ids)
                consume_qty += sum(product_order_line.product_uom_qty for product_order_line in product_order_line_ids)
            order_line.consumed_qty = consume_qty

    def compute_remain_delivery_qty(self):
        for record in self:
            record.remain_delivered_qty = record.product_uom_qty - record.delivered_qty

    def compute_delivery_qty(self):

        for order_line in self:
            delivered_qty = 0
            # print ('---------------------------------------------------')
            for sale_order in order_line.order_id.blanket_order_ids.filtered(lambda x: x.state != 'cancel'):
                # print ('--SALE ORDER')
                # print (sale_order.name)
                # print (order_line.product_id)
                product_order_line_ids = sale_order.order_line.filtered(lambda x: x.product_id == order_line.product_id)
                # print(product_order_line_ids)
                delivered_qty += sum(product_order_line.qty_delivered for product_order_line in product_order_line_ids)
            order_line.delivered_qty = delivered_qty


    remaining_qty = fields.Float(string='Remaining QTY', compute='compute_remaining_qty')
    consumed_qty = fields.Float(string='Consumed QTY', compute='compute_consume_qty')
    delivered_qty = fields.Float(string='Delivered QTY', compute='compute_delivery_qty')
    remain_delivered_qty = fields.Float(string='Pending QTY', compute='compute_remain_delivery_qty')
    period = fields.Integer(string='Frequency (Day)')
    standard_qty = fields.Integer(string='Standard Delivery')
    next_date = fields.Date(string='Next Order Date')
    next_delivery_date = fields.Date(string='Next Delivery Date')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: