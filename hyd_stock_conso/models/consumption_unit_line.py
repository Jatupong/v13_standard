# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class ConsumptionUnitLine(models.Model):

    _name = 'hyd_stock_conso.consumption_unit_line'
    _description = "Consumption Unit line"

    unit_id = fields.Many2one(
        string="Consumption unit",
        comodel_name="hyd_stock_conso.consumption_unit")

    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        required=True)

    product_qty = fields.Float(
        string='Quantity')

    date = fields.Date(
        string='Date',
        required=True)

    move_id = fields.Many2one(
        comodel_name='stock.move.line',
        string='Move Line',
        readonly=True)

    location_dest_id = fields.Many2one(
        comodel_name='stock.location',
        string='Destination',
        related='move_id.location_dest_id',
        store=True)

    @api.constrains('unit_id')
    def check_rule_ok(self):
        for record in self:
            rules = record.unit_id.rule_ids.filtered(
                lambda x: x.check_rule and record.date >= x.date_start and
                record.date <= x.date_end)
            for x in rules:
                status, message = x.check_move(record.product_id)
                if not status:
                    raise ValidationError(message)
