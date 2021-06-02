# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockReceiptJoin(models.TransientModel):
    _name = 'stock.receipt.join'
    _description = 'Stock Receipt Join'

    receipt_ids = fields.One2many('stock.receipt.lines',
                                  'stock_receipt_join_id', 'Receipt Line')

    @api.model
    def default_get(self, fields):
        # This method will fetch the picking lines in the wizard by default
        res = super(StockReceiptJoin, self).default_get(fields)
        lines = []
        pickings = self.env['stock.picking'].browse(
            self._context.get('active_ids', []))
        if any(picking.picking_type_code == 'outgoing'
               for picking in pickings):
            raise UserError(_('This operation can only be done for '
                              'Stock Receipt!'))
        for picking in pickings:
            for line in picking.move_lines:
                lines.append((0, 0, {'product_id': line.product_id.id,
                                     'description': line.name,
                                     'move_id': line.id,
                                     'order_number': line.picking_id.origin,
                                     'customer_id':
                                     line.picking_id.partner_id.id,
                                     'location_id': line.location_id.id,
                                     'product_uom_qty': line.product_uom_qty,
                                     'quantity': line.quantity_done
                                     }))
        res.update({'receipt_ids': lines})
        return res

    def join_receipt(self):
        '''
            this method will update source location and qty as per the user's
            selection and it will also validate the picking and create a
            backorder if the delivered qty is less than initial qty
        '''
        move_line_obj = self.env['stock.move.line']
        pickings = []
        for line in self.receipt_ids:
            if line.move_id.picking_id not in pickings:
                pickings.append((line.move_id.picking_id))
            line.move_id.write({'location_id': line.location_id.id,
                                'quantity_done': line.quantity})
            move_lines = move_line_obj.search([(
                'move_id', '=', line.move_id.id)])
            for move_line in move_lines:
                move_line.write({'location_id': line.location_id.id,
                                 'qty_done': line.quantity})
        for picking in pickings:
            # validating the picking
            validate = picking.button_validate()
            if validate and validate.get('res_id', False):
                if validate['res_model'] == 'stock.overprocessed.transfer':
                    wiz_id = self.env['stock.overprocessed.transfer']. \
                        browse(validate['res_id'])
                    wiz_id.action_confirm()
                # backorder creation
                elif validate['res_model'] == 'stock.backorder.confirmation':
                    wiz_id = self.env['stock.backorder.confirmation']. \
                        browse(validate['res_id'])
                    wiz_id.process()


class StockReceiptLines(models.TransientModel):
    _name = 'stock.receipt.lines'
    _description = 'Stock Receipt Lines'

    stock_receipt_join_id = fields.Many2one('stock.receipt.join')
    picking_id = fields.Many2one('stock.picking')
    move_id = fields.Many2one('stock.move')
    product_id = fields.Many2one('product.product', 'Product')
    description = fields.Char()
    order_number = fields.Char('Order Number')
    customer_id = fields.Many2one('res.partner', 'Customer')
    location_id = fields.Many2one('stock.location', 'Source Location')
    product_uom_qty = fields.Float('Initial Demand')
    quantity = fields.Float()
