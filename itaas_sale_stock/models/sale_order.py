# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Book)

from odoo import fields, api, models, _
from odoo.tools.misc import formatLang, get_lang
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare


class SaleOrder(models.Model):
    _inherit = "sale.order"

    is_validate_delivered = fields.Boolean(string='Delivery Validate', copy=False)
    state = fields.Selection(selection_add=[('delivery', 'Delivery')])

    def action_validate_delivered(self):
        self.write({'state':'delivery',
                    'is_validate_delivered':True,})


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    qty_backorder = fields.Float('Backorder Quantity', copy=False, compute='_compute_qty_delivered', compute_sudo=True, store=True,
                                 digits='Product Unit of Measure', default=0.0)
    backorder_price_subtotal = fields.Monetary(compute='_compute_qty_delivered', string='Backorder Subtotal', readonly=True, store=True)
    delivered_price_subtotal = fields.Monetary(compute ='_compute_qty_delivered', string='Delivered Subtotal', readonly=True, store=True)
    state = fields.Selection(selection_add=[('delivery', 'Delivery')])

    @api.depends('move_ids.state', 'move_ids.scrapped', 'move_ids.product_uom_qty', 'move_ids.product_uom')
    def _compute_qty_delivered(self):
        super(SaleOrderLine, self)._compute_qty_delivered()

        for line in self:  # TODO: maybe one day, this should be done in SQL for performance sake
            qty_backorder = backorder_price_subtotal = delivered_price_subtotal = 0.0
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            if line.qty_delivered_method == 'stock_move':
                qty = 0.0
                outgoing_moves, incoming_moves = line._get_outgoing_incoming_moves()
                for move in outgoing_moves:
                    if move.state != 'done':
                        continue
                    qty += move.product_uom._compute_quantity(move.product_uom_qty, line.product_uom, rounding_method='HALF-UP')
                for move in incoming_moves:
                    if move.state != 'done':
                        continue
                    qty -= move.product_uom._compute_quantity(move.product_uom_qty, line.product_uom, rounding_method='HALF-UP')
                # line.qty_delivered = qty
                qty_delivered = qty
                if qty_delivered <= line.product_uom_qty:
                    qty_backorder = line.product_uom_qty - qty_delivered
                    backorder_taxes = line.tax_id.compute_all(price, line.order_id.currency_id, qty_backorder,
                                                              product=line.product_id,
                                                              partner=line.order_id.partner_shipping_id)
                    backorder_price_subtotal = backorder_taxes['total_excluded']

                delivered_taxes = line.tax_id.compute_all(price, line.order_id.currency_id, qty_delivered,
                                                          product=line.product_id,
                                                          partner=line.order_id.partner_shipping_id)
                delivered_price_subtotal = delivered_taxes['total_excluded']

            line.update({'qty_backorder': qty_backorder,
                         'delivered_price_subtotal': delivered_price_subtotal,
                         'backorder_price_subtotal': backorder_price_subtotal, })

    @api.depends('qty_invoiced', 'qty_delivered', 'product_uom_qty', 'order_id.state')
    def _get_to_invoice_qty(self):
        """
        Compute the quantity to invoice. If the invoice policy is order, the quantity to invoice is
        calculated from the ordered quantity. Otherwise, the quantity delivered is used.
        """
        super(SaleOrderLine, self)._get_to_invoice_qty()
        for line in self:
            if line.order_id.state in ['sale','done','delivery']:
                if line.product_id.invoice_policy == 'order':
                    line.qty_to_invoice = line.product_uom_qty - line.qty_invoiced
                else:
                    line.qty_to_invoice = line.qty_delivered - line.qty_invoiced
            else:
                line.qty_to_invoice = 0

    @api.depends('state', 'product_uom_qty', 'qty_delivered', 'qty_to_invoice', 'qty_invoiced')
    def _compute_invoice_status(self):
        """
        Compute the invoice status of a SO line. Possible statuses:
        - no: if the SO is not in status 'sale' or 'done', we consider that there is nothing to
          invoice. This is also hte default value if the conditions of no other status is met.
        - to invoice: we refer to the quantity to invoice of the line. Refer to method
          `_get_to_invoice_qty()` for more information on how this quantity is calculated.
        - upselling: this is possible only for a product invoiced on ordered quantities for which
          we delivered more than expected. The could arise if, for example, a project took more
          time than expected but we decided not to invoice the extra cost to the client. This
          occurs onyl in state 'sale', so that when a SO is set to done, the upselling opportunity
          is removed from the list.
        - invoiced: the quantity invoiced is larger or equal to the quantity ordered.
        """
        super(SaleOrderLine, self)._compute_invoice_status()
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for line in self:
            if line.state not in ('sale','delivery','done'):
                line.invoice_status = 'no'
            elif not float_is_zero(line.qty_to_invoice, precision_digits=precision):
                line.invoice_status = 'to invoice'
            elif line.state in ('sale', 'delivery') and line.product_id.invoice_policy == 'order' and \
                    float_compare(line.qty_delivered, line.product_uom_qty, precision_digits=precision) == 1:
                line.invoice_status = 'upselling'
            elif float_compare(line.qty_invoiced, line.product_uom_qty, precision_digits=precision) >= 0:
                line.invoice_status = 'invoiced'
            else:
                line.invoice_status = 'no'
