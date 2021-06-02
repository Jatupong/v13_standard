# -*- coding: utf-8 -*-
from odoo import api, models, fields


# For some reason, odoo's views had trouble finding the category of the uom in sale.order.line on the fly
# This keeps the record in the DB, and allows me to filter UOM categories.
class NewPurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    # These computed fields are for calculating the domain on a form edit
    relcatid = fields.Many2one('uom.category',string='Related Cat ID')

    # related = 'product_uom.category_id'

    # The default onchange returns a domain, but it also does other stuff. Since we set a default domain, we want don't want it to return a domain
    # So we make a call to the original onchange, and just absorb the return value.  It still does all the other stuff
    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        # We call super and assign the return value to this variable. We do nothing with it, on purpose.
        self.relcatid = self.product_uom.category_id.id
        domain = super(NewPurchaseOrderLine, self).onchange_product_id()
        # the original function returned the above domain, but instead we return nothing and just use the default domain in the view
        return {}

# class NewPurchaseRequestLine(models.Model):
#     _inherit = 'purchase.request.line'
#
#     # These computed fields are for calculating the domain on a form edit
#     relcatid = fields.Many2one('uom.category', string='Related Cat ID')
#     product_uom_id = fields.Many2one('uom.uom')
#     # relcatid = fields.Many2one(related='product_uom_id.category_id', store=True)
#
#     # The default onchange returns a domain, but it also does other stuff. Since we set a default domain, we want don't want it to return a domain
#     # So we make a call to the original onchange, and just absorb the return value.  It still does all the other stuff
#     @api.multi
#     @api.onchange('product_id')
#     def onchange_product_id(self):
#         domain = super(NewPurchaseRequestLine, self).onchange_product_id()
#         # We call super and assign the return value to this variable. We do nothing with it, on purpose.
#         self.relcatid = self.product_uom_id.category_id.id
#         # the original function returned the above domain, but instead we return nothing and just use the default domain in the view
#         return {}
#
#
class PurchaseRequestLineMakePurchaseOrder(models.TransientModel):
    _inherit = "purchase.request.line.make.purchase.order"

    @api.model
    def _prepare_purchase_order_line(self, po, item):
        res = super(PurchaseRequestLineMakePurchaseOrder, self)._prepare_purchase_order_line(po, item)
        product_uom = item.product_uom_id or item.product_id.uom_po_id
        res['relcatid'] = product_uom.category_id.id

        return res

#     relcatid = fields.Many2one('uom.category', string='Related Cat ID')
#
#     @api.multi
#     @api.onchange('product_id')
#     def onchange_product_id(self):
#         domain = super(PurchaseRequestLineMakePurchaseOrderItem, self).onchange_product_id()
#         # We call super and assign the return value to this variable. We do nothing with it, on purpose.
#         # print('product_uom_id : ',self.product_uom_id.category_id.id)
#         self.relcatid = self.product_uom_id.category_id.id
#         # the original function returned the above domain, but instead we return nothing and just use the default domain in the view
#         return {}


