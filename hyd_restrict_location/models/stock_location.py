# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, Warning


class StockLocation(models.Model):

    _inherit = 'stock.location'

    allowed_users = fields.Many2many(
        string="Allowed Users",
        comodel_name='res.users',
        help="""Users allowed to do operation/move from/to this location"""
             """, others users will have a popup error on transfert action""")
