# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

ERROR_DELETE = "You cannot Delete %s because there is lines linked"

class ConsumptionUnit(models.Model):

    _name = 'hyd_stock_conso.consumption_unit'
    _order = 'complete_name'
    _description = "Consumption Unit"
    _rec_name = 'code'

    code = fields.Char(
    	string="Code")

    name = fields.Char(
    	string="Name")

    complete_name = fields.Char(
    	string="Full Location Name",
    	compute='_compute_complete_name',
    	store=True)

    type_unit = fields.Selection(
    	string="Unit type",
    	required=True,
    	selection=[
    		('normal', 'Regular'),
    		('view', 'View')],
    	default='normal')

    parent_path = fields.Char(index=True)

    parent_id = fields.Many2one(
        comodel_name='hyd_stock_conso.consumption_unit',
        string='Parent')

    locations_id = fields.Many2many(
        string="Locations",
        comodel_name="stock.location",
        relation="unit_m2m_location",
        required=True)

    line_ids = fields.One2many(
        comodel_name='hyd_stock_conso.consumption_unit_line',
        inverse_name='unit_id',
        string='Lines')

    rule_ids = fields.One2many(
        comodel_name='hyd_stock_conso.consumption_rule',
        inverse_name='unit_id',
        string='Rules')

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
    	for rec in self:
        	""". """
	        if rec.parent_id.complete_name:
	            rec.complete_name = '%s/%s' % (rec.parent_id.complete_name, rec.name)
	        else:
	            rec.complete_name = rec.name

    def unlink(self):
        for unit in self:
            if unit.line_ids:
                raise ValidationError(_(ERROR_DELETE % unit.name))
        return super(ConsumptionUnit, self).unlink()
