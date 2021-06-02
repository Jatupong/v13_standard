# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _

from odoo.exceptions import AccessError, UserError, ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _get_order_type(self):


        # user_id = self.env['res.users'].browse(self.env.uid)
        type_ids = self.env['sale.order.type'].search([])
        # print ('----XXX TYPE')
        # print (user_id)

        # if user_id and user_id.sale_type:
        #     return user_id.sale_type
        # if not user_id.sale_type:
        #     if self.partner_id.sale_type:
        #         return self.partner_id.sale_type
        #     if not self.partner_id.sale_type:
        #         return user_id.sale_type or False
        if type_ids:
            return type_ids[0]
        else:
            return False


    type_id = fields.Many2one(
        comodel_name='sale.order.type', string='Type', default=_get_order_type)

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        super(SaleOrder, self).onchange_partner_id()
        user_id = self.env['res.users'].browse(self.env.uid)
        if not user_id.sale_type:
            sale_type = (self.partner_id.sale_type or
                         self.partner_id.commercial_partner_id.sale_type)
            if sale_type:
                self.type_id = sale_type
        ############### Since other parameter of order type change but something overwrite, so need this function to update other parameter of order type
        self.onchange_type_id()



    @api.onchange('type_id')
    def onchange_type_id(self):
        for order in self:
            # if order.type_id.warehouse_id:
            #     order.warehouse_id = order.type_id.warehouse_id
            # if order.type_id.picking_policy:
            #     order.picking_policy = order.type_id.picking_policy
            if order.type_id.payment_term_id:
                order.payment_term_id = order.type_id.payment_term_id.id
            if order.type_id.pricelist_id:
                order.pricelist_id = order.type_id.pricelist_id.id
            # if order.type_id.incoterm_id:
            #     order.incoterm = order.type_id.incoterm_id.id
            if order.type_id.account_analytic_account:
                order.analytic_account_id = order.type_id.account_analytic_account.id


    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/'and vals.get('type_id'):
            sale_type = self.env['sale.order.type'].browse(vals['type_id'])
            if sale_type.sequence_id:
                vals['name'] = sale_type.sequence_id.next_by_id()
        return super(SaleOrder, self).create(vals)


    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        if self.type_id.journal_id:
            res['journal_id'] = self.type_id.journal_id.id
        if self.type_id:
            res['sale_type_id'] = self.type_id.id
        if self.date_order:
            res['invoice_date'] = self.date_order
        return res


    def action_confirm(self):
        if self.date_order:
            date_temp = self.date_order
            res = super(SaleOrder, self).action_confirm()
            self.update({'date_order': date_temp})
            return res
        else:
            return super(SaleOrder,self).action_confirm()

