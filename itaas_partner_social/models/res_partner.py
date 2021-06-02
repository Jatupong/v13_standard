# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class Partner(models.Model):
    _inherit = "res.partner"

    instagram = fields.Char(string='IG')
    line = fields.Char(string='Line')
    facebook = fields.Char(string='Facebook')
    location = fields.Char(string='Location')
    note_for_inventory = fields.Char(string='Note for Delivery')
