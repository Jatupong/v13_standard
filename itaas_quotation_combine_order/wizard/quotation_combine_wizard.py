# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Book)

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class QuotationCombineWizard(models.TransientModel):
    _name = 'quotation.combine.wizard'

    partner_id = fields.Many2one('res.partner', string="Partner")
    contact = fields.Many2one('res.partner', string="Contact")
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company)
    payment_term_id = fields.Many2one('account.payment.term', string='Payment Terms', required=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", )
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist',required=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="If you change the pricelist, only newly added lines will be affected.")
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account',
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="The analytic account related to a sales order.")
    date_order = fields.Datetime(string='Order Date', required=True,
                                 help="Creation date of draft/sent orders,\nConfirmation date of confirmed orders.")

    @api.model
    def default_get(self, fields_list):
        res = super(QuotationCombineWizard, self).default_get(fields_list)
        sale = self.env['sale.order'].browse(self.env.context.get('active_ids')[0])
        res.update({'partner_id': sale.partner_id.id,
                    'contact': sale.contact.id,
                    'payment_term_id': sale.payment_term_id.id,
                    'pricelist_id': sale.pricelist_id.id,
                    'analytic_account_id': sale.analytic_account_id.id,
                    'date_order': sale.date_order,
                    })
        return res

    def action_combine_order(self):
        sale = self.env['sale.order'].browse(self.env.context.get('active_ids'))
        first_sale = sale[0]
        sales = sale[1:]
        sale_line_ids = sales.mapped('order_line')

        order_line = []
        for line in sale_line_ids:
            val_line = self._prepare_order_line(line)
            order_line.append((0, 0,val_line))
        #
        # val = self._prepare_order(first_sale)
        # val['order_line'] = order_line
        first_sale.update({'order_line': order_line})
        new_sale_id = first_sale

        if new_sale_id:
            # print('new_sale_id : ',new_sale_id)
            # print('new_sale_id.state : ',new_sale_id.state)
            ori_first_sale = new_sale_id.name
            new_sale_id.action_confirm()
            # print('new_sale_id.state : ', new_sale_id.state)
            # print('ori_first_sale : ', ori_first_sale)
            body_message = 'Combine : ' + str(ori_first_sale) + ', '
            check = False
            for order in sales:
                if check:
                    body_message += ', '
                body_message += ('<a href=# data-oe-model=sale.order data-oe-id=%d>%s</a>') % (order.id, order.name)
                check = True
                order.action_cancel()
                order.write({'combine_order_id': new_sale_id.id,
                             'active': False})

            new_sale_id.message_post(body=body_message)
            view_form_id = self.env.ref('sale.view_order_form').id
            action = self.env.ref('sale.action_orders').read()[0]
            action.update({
                'views': [(view_form_id, 'form')],
                'view_mode': 'form',
                'name': new_sale_id.name,
                'res_id': new_sale_id.id,
            })

            return action

    def _prepare_order_line(self, line):
        val_line = {
            'name': line.name,
            'product_id': line.product_id.id,
            'product_uom_qty': line.product_uom_qty,
            'product_uom': line.product_uom.id,
            'price_unit': line.price_unit,
            'tax_id': line.tax_id,
            'discount': line.discount,
            'discount_ontop1': line.discount_ontop1,
            'discount_ontop2': line.discount_ontop2,
            'discount_ontop3': line.discount_ontop3,
            'customer_lead': line.customer_lead,
        }

        return val_line

    def _prepare_order(self, order):
        val = {
            'partner_id': order.partner_id.id,
            'partner_invoice_id': order.partner_invoice_id.id,
            'partner_shipping_id': order.partner_shipping_id.id,
            'contact': self.contact.id,
            'payment_term_id': self.payment_term_id.id,
            'pricelist_id': self.pricelist_id.id,
            'analytic_account_id': self.analytic_account_id.id,
            'date_order': self.date_order,}

        return val