# Copyright 2017-2020 Forgeflow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    project_id = fields.Many2one('project.project','Project')