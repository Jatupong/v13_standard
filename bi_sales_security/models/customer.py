# -*- coding : utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class ResPartner(models.Model):
    _inherit = "res.partner"

    allowed_user_ids = fields.Many2many('res.users', 'res_partner_users_sale_rel', string="Allowed Users")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: