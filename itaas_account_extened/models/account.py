# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Book)

from odoo import fields, api, models, _


class Account(models.Model):
    _inherit = 'account.move'

    delivery_date = fields.Date('Delivery Date')