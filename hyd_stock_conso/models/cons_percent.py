# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ConsumptionUnit(models.Model):

    _name = 'hyd_stock_conso.cons_percent'
    _description = "Consumption Unit Percent"
    _rec_name = 'code'

    code = fields.Char(
    	string="Code")

    name = fields.Char(
    	string="Libelle")

    ratio = fields.Float(
        string='Ratio pourcentage',
        default=0.0)
