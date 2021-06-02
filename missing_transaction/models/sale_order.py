
from odoo import api, models, fields

class sale_order(models.Model):
    _inherit = "sale.order"

    transaction_number = fields.Char(string="Transaction")
    

