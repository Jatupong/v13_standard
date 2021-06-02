# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Book)

from odoo import fields, api, models, _


class res_partner(models.Model):
    _inherit = "res.partner"

    fax = fields.Char(String='Fax')