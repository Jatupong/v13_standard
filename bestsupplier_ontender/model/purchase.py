# -*- coding: utf-8 -*-
# Copyright (c) 2015-Present TidyWay Software Solution. (<https://tidyway.in/>)

from odoo import fields, models, api, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import Warning


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'


    def _compute_bid_subtotal(self):
        for line in self:
            line.bid_subtotal = line.quantity_bid * line.price_unit

    quantity_bid = fields.Float(
        string='Quantity Bid',
        digits=dp.get_precision('Product Unit of Measure'),
        help="Technical field for not loosing "
        "the initial information about the quantity proposed in the bid"
        )
    bid_subtotal = fields.Float(
        compute="_compute_bid_subtotal",
        strign='To Subtotal',
        digits=dp.get_precision('Product Unit of Measure')
        )
    internal_state = fields.Selection([
        ('draft', 'Draft'),
        ('positive', 'Positive'),
        ('lock', 'Locked'),
        ], string='Status', readonly=True, copy=False, default='draft')


    def action_internal_draft(self):
        self.write({
                    'internal_state': 'draft',
                    'quantity_bid': 0.0
                    })


    def action_internal_confirm(self):
        self.write({
                    'quantity_bid': self.product_qty,
                    'internal_state': 'lock'
                    })


class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"

    @api.model
    def _get_purchase_line_ids(self, tender):
        line_obj = self.env['purchase.order.line']
        total_lines = []
        for requisition in tender:
            for po in requisition.purchase_ids.filtered(lambda purchase_order: purchase_order.state not in ['cancel']):
                line_obj |= po.order_line
                total_lines += [po_line.id for po_line in po.order_line]
        return line_obj


    def action_internal_draft(self):
        self.write({'internal_state': 'draft'})


    def action_internal_confirm(self):
        self.write({'internal_state': 'lock'})


    def action_open(self):
        for record in self:
            if not record.purchase_ids:
                raise Warning(_('At least one supplier quote '
                                'should be generated.\n Please click '
                                'to "New Quotation" button to generate a '
                                'quote for supplier'))
        return super(PurchaseRequisition, self).action_open()


    def open_bid_lines(self):
        """ This opens product line view to view 
            all lines from the different quotations, 
            groupby default by product and partner to show comparaison
            between supplier price
            @return: the product line tree view
        """
        action_lines = self.env.ref('bestsupplier_ontender.action_purchase_linetree')
        action = action_lines.read()[0]
        action['context'] = {
            'search_default_groupby_product': True,
            'search_default_hide_cancelled': True,
            'tender_id': self.id,
        }
        po_lines = []
        for po in self.purchase_ids.filtered(lambda purchase_order:
                                             purchase_order.state not in
                                             ['cancel']):
            po_lines += [po_line.id for po_line in po.order_line]
        action['domain'] = [('id', 'in', po_lines)]
        return action

    @api.model
    def check_valid_quotation(self, quotation):
        """
        Check if a quotation has all his order lines bid in order to confirm it if its the case
        return True if all order line have been selected during bidding process, else return False

        args : 'quotation' must be a browse record
        """
        for line in quotation.order_line:
            if line.internal_state not in ('lock', 'positive') or line.product_qty != line.quantity_bid:
                return False
        return True

    @api.model
    def _prepare_po_from_tender(self, tender_id, tender_name):
        return {
                'order_line': [],
                'requisition_id': tender_id,
                'origin': tender_name
                }

    @api.model
    def _prepare_po_line_from_tender(self, quantity_bid, purchase_id):
        return {
                'product_qty': quantity_bid,
                'order_id': purchase_id
                }

    @api.model
    def cancel_unconfirmed_quotations(self, tender):
        #cancel other orders
        for quotation in tender.purchase_ids:
            if quotation.state in ['draft', 'sent']:
                quotation.button_cancel()
                quotation.message_post(
                   body=_('Cancelled by the call for bids associated '
                          'to this request for quotation.'))
        return True


    def generate_po(self):
        """
        Generate all purchase order based on selected lines, 
            should only be called on one tender at a time
        """
        po = self.env['purchase.order']
        id_per_supplier = {}
        total_pos = []
        for tender in self:
            if tender.state == 'done':
                raise Warning(_('You have already generate the purchase order(s).'))
            confirm = False
            #check that we have at least confirm one line
            total_polines = self._get_purchase_line_ids(tender)
            for po_line in total_polines:
                if po_line.internal_state in ('lock', 'positive'):
                    confirm = True
                    break
            if not confirm:
                raise Warning(_('You have no line selected for buying.'))

            #check for complete RFQ
            for quotation in tender.purchase_ids:
                if self.check_valid_quotation(quotation):
                    #use workflow to set PO state to confirm
                    quotation.button_confirm()

            #get other confirmed lines per supplier
            for po_line in total_polines:
                #only take into account confirmed line that does not belong to already confirmed purchase order
                if po_line.internal_state in ('lock', 'positive') and\
                     po_line.order_id.state in ['draft', 'sent']:
                    if id_per_supplier.get(po_line.partner_id.id):
                        id_per_supplier[po_line.partner_id.id].append(po_line)
                    else:
                        id_per_supplier[po_line.partner_id.id] = [po_line]

            #generate po based on supplier and cancel all previous RFQ
            ctx = dict(self._context or {}, force_requisition_id=True)
            for supplier, product_line in id_per_supplier.items():
                #copy a quotation for this supplier and change order_line then validate it
                quotation_id = po.search([
                                          ('requisition_id', '=', tender.id),
                                          ('partner_id', '=', supplier)],
                                         limit=1)

                vals = self._prepare_po_from_tender(tender.id, tender.name)
                new_po = quotation_id.copy(default=vals)
                #duplicate po_line and change product_qty if needed and associate them to newly created PO
                for line in product_line:
                    vals = self._prepare_po_line_from_tender(
                                                             line.quantity_bid,
                                                             new_po.id
                                                             )
                    line.copy(default=vals)
                #use workflow to set new PO state to confirm
                new_po.button_confirm()
                total_pos.append(new_po.id)

            #cancel other orders
            self.cancel_unconfirmed_quotations(tender)
            #set tender to state done
            tender.action_done()

        tree_id = self.env.ref(
                   'purchase.purchase_order_tree').id
        form_id = self.env.ref(
                   'purchase.purchase_order_form').id

        return {
            'domain': str([('id', 'in', total_pos)]),
            'name': _('Approved Orders'),
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            'type': 'ir.actions.act_window',
            'views': [(tree_id, 'tree'), (form_id, 'form')],
            'target': 'current'
        }
