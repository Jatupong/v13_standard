# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare


# class stock_move(models.Model):
#     _inherit = 'stock.move'
#
#     rm_fg_cal_qty = fields.Float(string='RM qty already cal to FG')
#     cost_already_recorded = fields.Boolean(string='Cost already record',default=False)
#     #don't use yet.
#     # max_fg_qty = fields.Integer(string='Max FG Qty')

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    is_material_consume = fields.Boolean(string='Material Consumed First',default=True) #if post as odoo standard

    @api.depends('move_raw_ids.state', 'move_finished_ids.state', 'workorder_ids', 'workorder_ids.state',
                 'qty_produced', 'move_raw_ids.quantity_done', 'product_qty')
    def _compute_state(self):
        for production in self:
            if production.is_material_consume and production.move_finished_ids.filtered(
                lambda m: m.state not in ('cancel', 'done') and m.product_id.id == production.product_id.id) \
                and (production.qty_produced >= production.product_qty) \
                and (not production.routing_id or all(
                wo_state in ('cancel', 'done') for wo_state in production.workorder_ids.mapped('state'))):
                production.state = 'to_close'

            else:
                super(MrpProduction, production)._compute_state()

    def update_accounting_entry(self):
        for production_id in self:
            move_raw_ids = production_id.move_raw_ids.filtered(lambda x: x.state == 'done' and x.quantity_done > 0)
            move_finished_ids = production_id.move_finished_ids.filtered(lambda x: x.state == 'done' and x.quantity_done > 0)
            # all_stock_move = move_raw_ids + move_finished_ids
            fg_value = 0
            # print (move_raw_ids)
            for stock_move in move_raw_ids:
                fg_value += abs(stock_move.stock_valuation_layer_ids[0].value)
                stock_move.delete_account_entry_action_done()
                stock_move.update_account_entry_action_done()

            fg_unit_value = fg_value / production_id.product_qty
            for stock_move in move_finished_ids:
                stock_move.delete_account_entry_action_done()
                stock_move.stock_valuation_layer_ids[0].unit_cost = fg_unit_value
                stock_move.stock_valuation_layer_ids[0].value = fg_unit_value * stock_move.stock_valuation_layer_ids[0].quantity
                stock_move.stock_valuation_layer_ids[0].remaining_value = fg_unit_value * stock_move.stock_valuation_layer_ids[
                    0].remaining_qty
                stock_move.update_account_entry_action_done()


            production_id._direct_cost_postings()


    def post_inventory(self):
        for order in self:
            # print (x)
            order.consume_material_to_wip()
            order._direct_cost_postings()
            super(MrpProduction, order).post_inventory()
        return True


    def _direct_cost_postings(self):
        print ('--_direct_cost_postings---')
        move_raw_ids = self.move_raw_ids.filtered(lambda x: x.state == 'done' and x.quantity_done > 0 and x.product_type == 'consu')
        for record in move_raw_ids:
            # print ('ST1')
            desc_wo = record.product_id.name

            amount = round(record.stock_valuation_layer_ids[0].value, 2)
            if amount:
                id_created_header = self.env['account.move'].create({
                    'journal_id' : record.product_id.categ_id.property_stock_journal.id,
                    'date': fields.datetime.today(),
                    'ref' : desc_wo,
                    'stock_move_id': record.id,
                    'company_id': record.production_id.company_id.id,
                })
                # print('ST11')
                account_id = record.product_id.categ_id.property_stock_account_output_categ_id

                val_id_credit_item = {
                    'move_id' : id_created_header.id,
                    'account_id': account_id.id,
                    'product_id': self.product_id.id,
                    'name' : desc_wo,
                    'quantity': record.product_uom_qty,
                    'product_uom_id': record.product_uom.id,
                    'credit': abs(amount) if amount < 0 else 0.00,
                    'debit': abs(amount) if amount > 0 else 0.00,
                    'manufacture_order_id': self.id,

                }

                id_credit_item = self.env['account.move.line'].with_context(check_move_validity=False).create(val_id_credit_item)

                account_id = self.product_id.property_stock_production.with_context(force_company=record.production_id.company_id.id).valuation_in_account_id

                if not account_id:
                    account_id = self.product_id.categ_id.property_stock_account_input_categ_id

                print ('ACCOUNT')
                print (amount)
                print (account_id)
                val_id_debit_item = {
                    'move_id' : id_created_header.id,
                    'account_id': account_id.id,
                    'product_id': self.product_id.id,
                    'name' : desc_wo,
                    'quantity': record.product_uom_qty,
                    'product_uom_id': record.product_uom.id,
                    'debit': abs(amount) if amount < 0 else 0.00,
                    'credit': abs(amount) if amount > 0 else 0.00,
                    'manufacture_order_id': self.id,
                }
                print ('DEBIT - CREDIT')
                print (val_id_credit_item)
                print (val_id_debit_item)
                id_debit_item= self.env['account.move.line'].with_context(check_move_validity=False).create(val_id_debit_item)

                id_created_header.post()
        return True

    def _cal_price(self, consumed_moves):
        for production_id in self:
            super(MrpProduction, production_id)._cal_price(consumed_moves)
            fg_value = 0
            fg_done_value = 0
            move_raw_ids = production_id.move_raw_ids.filtered(lambda x: x.state == 'done' and x.quantity_done > 0)
            for stock_move in move_raw_ids:
                fg_value += abs(stock_move.stock_valuation_layer_ids.value)

            # print ('FG VaLUE')
            # print (fg_value)

            finished_move = self.move_finished_ids.filtered(lambda x: x.product_id == self.product_id and x.state not in ('done', 'cancel') and x.quantity_done > 0)
            finished_move_done_ids = self.move_finished_ids.filtered(
                lambda x: x.product_id == self.product_id and x.state =='done' and x.quantity_done > 0)

            for fg_move in finished_move_done_ids:
                fg_done_value += abs(fg_move.stock_valuation_layer_ids.value)

            finished_move.price_unit = (fg_value-fg_done_value)/ finished_move.quantity_done


    def consume_material_to_wip(self):
        for order in self:
            if not order.is_material_consume:
                continue
            else:
                moves_not_to_do = order.move_raw_ids.filtered(lambda x: x.state == 'done')
                moves_to_do = order.move_raw_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
                for move in moves_to_do.filtered(lambda m: m.product_qty == 0.0 and m.quantity_done > 0):
                    move.product_uom_qty = move.quantity_done

                moves_to_do._action_done()


                ######### additional moves_to_do
                moves_to_do = order.move_raw_ids.filtered(lambda x: x.state == 'done') - moves_not_to_do
                print (moves_to_do)
                #########
                # order._cal_price(moves_to_do)


                order.workorder_ids.mapped('raw_workorder_line_ids').unlink()
                order.action_assign()


class MrpProductProduce(models.TransientModel):
    _inherit = "mrp.product.produce"

    def _record_production(self):
        super(MrpProductProduce, self)._record_production()
        for produce in self:
            produce.production_id.consume_material_to_wip()