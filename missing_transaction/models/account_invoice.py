from odoo import models, fields

class account_invoice(models.Model):
    _inherit = "account.move"

    transaction_number = fields.Char(string="Transaction")
    

