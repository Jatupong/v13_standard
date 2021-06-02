# -*- coding: utf-8 -*-
from odoo.tests import common
from odoo.exceptions import ValidationError
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)


class TestTransfert(common.TransactionCase):

    post_install = True

    def setUp(self):

        super(TestTransfert, self).setUp()

        # cree l'entrepot
        self.entrepot = self.env["stock.warehouse"].create(
            {'name': 'TEST_WAREHOUSE', 'code': 'TEST'})

        self.default_location = self.entrepot.mapped("view_location_id")

        # cree emplacement 1
        self.location1 = self.env["stock.location"].create({
            'name': 'LOCATION TEST 1',
            'location_id': self.default_location.id,
            'usage': 'internal'})

        # cree emplacement 2
        self.location2 = self.env["stock.location"].create({
            'name': 'LOCATION TEST 2',
            'location_id': self.default_location.id,
            'usage': 'internal'})

        # create 1 article
        self.article = self.env['product.product'].create({
            'name': 'article test',
            # 'sale_ok': True,
            'type': 'product'})
        self.article.sale_ok = True

        # create a new sequence for picking type
        sequence = self.env["ir.sequence"].create({
            'name': "Test entrepot",
            'code': "stock.picking",
            'prefix': "TESTSTOCKPICKING",
            'padding': 2,
            'number_increment': 1,
            'number_next_actual': 1,
            'implementation': 'standard'})

        # create a new picking type
        self.picking_type = self.env["stock.picking.type"].create({
            'name': "TYPE PICKING TEST",
            'code': 'internal',
            'sequence_id': sequence.id,
            'warehouse_id': self.entrepot.id})

        self.env['stock.quant']._update_available_quantity(
            self.article, self.location1, 100)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(
            self.article, self.location1), 100.0)

        # cree les utilisateurs de test
        self.user1 = self.env["res.users"].create({
            'name': 'Utilisateur 1',
            'login': 'user01@test.com',
            'email': 'user01@test.com'})

        self.user2 = self.env["res.users"].create({
            'name': 'Utilisateur 2',
            'login': 'user02@test.com',
            'email': 'user02@test.com'})

        group_user_warehouse = self.env.ref("stock.group_stock_user")
        group_user_warehouse.users |= self.user1
        group_user_warehouse.users |= self.user2

    @common.post_install(True)
    def test_create_all_object(self):
        """Teste la creation d'une unite de consommation."""

        # create a new unit
        unit = self.env["hyd_stock_conso.consumption_unit"].sudo().create({
            'code': "CEO",
            'name': "Chief of executive"})
        unit.locations_id |= self.location2
        self.assertEqual(unit.id, True)

        percent = self.env["hyd_stock_conso.cons_percent"].sudo().create({
            'code':"80%",
            'name': "80%",
            'ratio': "0.8"})
        self.assertEqual(percent.id, True)

        today = datetime.now()
        rule = self.env["hyd_stock_conso.consumption_rule"].sudo().create({
            'unit_id': unit.id,
            'date_start': today.strftime("%Y-%m-01"),
            'date_end': today.strftime("%Y-%m-30")})
        self.assertEqual(rule.id, True)

        rule_line = self.env["hyd_stock_conso.consumption_rule_line"].sudo().create({
            'rule_id': rule.id,
            'product_id': self.article.id,
            'product_qty': 5})
        self.assertEqual(rule_line, True)

    @common.post_install
    def test_track_quota(self):
        """test the quota tracking of the stock.""" 
        # create a new unit
        unit = self.env["hyd_stock_conso.consumption_unit"].sudo().create({
            'code': "CEO",
            'name': "Chief of executive"})
        unit.locations_id |= self.location2

        percent = self.env["hyd_stock_conso.cons_percent"].sudo().create({
            'code':"80%",
            'name': "80%",
            'ratio': "0.8"})

        today = datetime.now()
        rule = self.env["hyd_stock_conso.consumption_rule"].sudo().create({
            'unit_id': unit.id,
            'date_start': today.strftime("%Y-%m-01"),
            'date_end': today.strftime("%Y-%m-30")})

        rule_line = self.env["hyd_stock_conso.consumption_rule_line"].sudo().create({
            'rule_id': rule.id,
            'product_id': self.article.id,
            'product_qty': 5})

        # create a new transfert
        transfert = self.env["stock.picking"].sudo(self.user1).create({
            'picking_type_id': self.picking_type.id,
            'location_id': self.location1.id,
            'location_dest_id': self.location2.id})

        move = self.env["stock.move"].sudo(self.user1).create({
            'product_id': self.article.id,
            'product_uom': 1,
            'product_uom_qty': 4,
            'name': self.article.name,
            'picking_id': transfert.id,
            'location_id': self.location1.id,
            'location_dest_id': self.location2.id})
        move.consump_units |= unit
        move.consump_percent |= percent

        # confirme le mouvement
        self.assertEqual(transfert.state, "confirmed")
        self.assertEqual(transfert.state, "assigned")
        backorder_wizard_dict = transfert.button_validate()
        backorder_wizard = self.env[backorder_wizard_dict[
            'res_model']].browse(backorder_wizard_dict['res_id'])
        backorder_wizard.process()

        lines = rules.line_ids
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0].product_id.id, self.article.id)
        self.assertEqual(lines[0].product_qty, 4)



    # @common.post_install(True)
    # def test_create_rule(self):
    #     """Teste la creation d'un transfert."""

    #     # create a new transfert
    #     transfert = self.env["stock.picking"].sudo(self.user1).create({
    #         'picking_type_id': self.picking_type.id,
    #         'location_id': self.location1.id,
    #         'location_dest_id': self.location2.id})

    #     move = self.env["stock.move"].sudo(self.user1).create({
    #         'product_id': self.article.id,
    #         'product_uom': 1,
    #         'product_uom_qty': 100,
    #         'name': self.article.name,
    #         'picking_id': transfert.id,
    #         'location_id': self.location1.id,
    #         'location_dest_id': self.location2.id})

    #     transfert.action_assign()
    #     self.assertEqual(transfert.state, "assigned")

    #     backorder_wizard_dict = transfert.button_validate()
    #     backorder_wizard = self.env[backorder_wizard_dict[
    #         'res_model']].browse(backorder_wizard_dict['res_id'])
    #     backorder_wizard.process()

    #     transfert.action_done()
    #     transfert.action_assign()
    #     backorder_wizard_dict = transfert.button_validate()
    #     backorder_wizard = self.env[backorder_wizard_dict[
    #         'res_model']].browse(backorder_wizard_dict['res_id'])
    #     backorder_wizard.process()
    #     transfert.action_done()


    #     self.assertEqual(transfert.state, "done")

    # @common.post_install(True)
    # def test_path_onchange_picking(self):
    #     """Teste l'utilisation de path dans le transfert."""

    #     # create a new transfert
    #     pre_transfert = self.env["stock.picking"].sudo(self.user1).new({
    #         'picking_type_id': self.picking_type.id,
    #         'path_id': self.path_1.id})
    #     pre_transfert.sudo(self.user1)._onchange_path_id()
    #     self.assertEqual(pre_transfert.location_id.id, self.location1.id)
    #     self.assertEqual(pre_transfert.location_dest_id.id, self.location2.id)

    #     transfert = self.env["stock.picking"].sudo(self.user1).create({
    #         'picking_type_id': self.picking_type.id,
    #         'path_id': self.path_1.id,
    #         'location_id': pre_transfert.location_id.id,
    #         'location_dest_id': pre_transfert.location_dest_id.id
    #     })

    #     self.assertEqual(transfert.location_id.name, self.location1.name)

    #     move = self.env["stock.move"].sudo(self.user1).create({
    #         'product_id': self.article.id,
    #         'product_uom': 1,
    #         'product_uom_qty': 100,
    #         'name': self.article.name,
    #         'picking_id': transfert.id,
    #         'location_id': self.location1.id,
    #         'location_dest_id': self.location2.id})

    #     # confirme le mouvement
    #     transfert.action_confirm()
    #     self.assertEqual(transfert.state, "confirmed")

    #     transfert.action_assign()
    #     self.assertEqual(transfert.state, "assigned")

    #     backorder_wizard_dict = transfert.button_validate()
    #     backorder_wizard = self.env[backorder_wizard_dict[
    #         'res_model']].browse(backorder_wizard_dict['res_id'])
    #     backorder_wizard.process()

    #     transfert.action_done()
    #     self.assertEqual(transfert.state, "done")
