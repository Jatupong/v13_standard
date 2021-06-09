# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.tools.float_utils import float_is_zero


class Customer_billing_inherit(models.Model):
    _inherit = 'customer.billing'

    @api.onchange('partner_id')
    @api.depends('partner_id')
    def onchange_partner_id(self):
        print('===onchange_partner_id===')
        xxx_ids = self.env['account.move'].search(['|',('bill_to_id','=',self.partner_id.id),('partner_id','=',self.partner_id.id),('state','=','posted'),('billing_id','=',False),('type','=','out_invoice'),
                                                      ('invoice_date_due','<=',self.date_billing),('company_id','=',self.company_id.id)])
        print('partner_id:',self.partner_id)
        print('xxx_ids:',xxx_ids)
        if self.type == 'out_invoice':
            if self.auto_load:
                inv_ids = self.env['account.move'].search(['|',('bill_to_id','=',self.partner_id.id),('partner_id','=',self.partner_id.id),('state','=','posted'),('billing_id','=',False),('type','=','out_invoice'),
                                                              ('invoice_date_due','<=',self.date_billing),('company_id','=',self.company_id.id)])

                inv_ids = [inv.id for inv in inv_ids]
                self.invoice_ids = [(6, 0, inv_ids)]
            self.customer_supplier = 'customer'

        elif self.type == 'in_invoice':
            # print "y"
            if self.auto_load:
                inv_ids = self.env['account.move'].search(
                    [('state', '=', 'posted'), ('type', '=', 'in_invoice'), ('billing_id', '=', False),
                     ('partner_id', '=', self.partner_id.id), ('invoice_date_due','<=',self.date_billing),('company_id', '=', self.company_id.id)])
                inv_ids = [inv.id for inv in inv_ids]
                self.invoice_ids = [(6, 0, inv_ids)]
            self.customer_supplier = 'supplier'


