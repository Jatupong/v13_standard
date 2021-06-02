# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api


class SalesOrderLine(models.Model):
    _inherit = 'sale.order.line'

    number = fields.Integer()


class SalesOrder(models.Model):
    _inherit = 'sale.order'

    is_number_line = fields.Boolean(compute='get_number', store=True, compute_sudo=True)

    @api.depends('order_line', 'order_line.sequence')
    def get_number(self):
        for obj in self:
            number = 1
            for line in obj.order_line.filtered(lambda x: x.product_id).sorted(lambda x: x.sequence):
                line.number = number
                number += 1
            obj.is_number_line = True