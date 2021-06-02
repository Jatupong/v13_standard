# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Book)


from odoo import api, fields, models, _
from odoo.exceptions import UserError


class Partner(models.Model):
    _inherit = "res.partner"

    note_for_delivery = fields.Char(string='Note for Delivery')
