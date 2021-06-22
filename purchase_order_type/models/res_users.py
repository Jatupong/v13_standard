# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Book)

from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    purchase_type = fields.Many2one('purchase.order.type', string='Purchase Order Type',)