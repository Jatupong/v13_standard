# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
OVER_LIMIT = _("""The product %s for the unit %s is """
             """limited in this period to %.2f but your """
             """actual consumption is %.2f """)

class ConsumptionRule(models.Model):

    _name = 'hyd_stock_conso.consumption_rule'
    _description = "Consumption Rule"

    name = fields.Char(
        string="Name",
        required=True)

    unit_id = fields.Many2one(
        string="Consumption unit",
        comodel_name="hyd_stock_conso.consumption_unit")

    date_start = fields.Date(
        string='Date start')

    date_end = fields.Date(
        string='Date end')

    check_rule = fields.Boolean(
        string='Check rule',
        default=True)

    line_ids = fields.One2many(
        comodel_name='hyd_stock_conso.consumption_rule_line',
        inverse_name='rule_id',
        string='Lines')

    @api.model
    def check_move(self, product_id):
        consomptions = sum(self.unit_id.line_ids.filtered(
            lambda x: x.product_id.id == product_id.id and
            x.date >= self.date_start and x.date <= self.date_end).mapped(
            'product_qty'))

        pro_lines = self.line_ids.filtered(
            lambda x: x.product_id.id == product_id.id)
        consomption_limit = sum(pro_lines.mapped('product_qty'))

        status = consomption_limit >= consomptions if pro_lines and consomption_limit > -1 else True
        if not status:
            message = OVER_LIMIT % (
                product_id.name,
                self.unit_id.name,
                consomption_limit,
                consomptions)
            return status, message
        else:
            return status, ""


class ConsumptionRuleLine(models.Model):

    _name = 'hyd_stock_conso.consumption_rule_line'
    _description = "Consumption Rule Line"

    rule_id = fields.Many2one(
        string="Consumption Rule",
        comodel_name="hyd_stock_conso.consumption_rule")

    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        required=True)

    product_qty = fields.Float(
        string='Quantity to limit',
        default=-1)

    actual_qty = fields.Float(
        string='Actual Quantity',
        compute="compute_actual_qty")

    remain_qty = fields.Float(
        string='Remain Quantity',
        compute="compute_actual_qty")

    def compute_actual_qty(self):
        for rec in self:
            consomptions = sum(rec.rule_id.unit_id.line_ids.filtered(
                lambda x: x.product_id.id == rec.product_id.id and
                x.date >= rec.rule_id.date_start and x.date <= rec.rule_id.date_end).mapped(
                'product_qty'))
            rec.actual_qty = consomptions
            rec.remain_qty = rec.product_qty - rec.actual_qty

