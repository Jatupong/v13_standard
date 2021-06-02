# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

ERROR_RATIO = _("BAD SUM RATE")

class StockMoveLine(models.Model):

    _inherit = 'stock.move.line'
    _name = 'stock.move.line'

    consump_units = fields.Many2many(
        comodel_name='hyd_stock_conso.consumption_unit',
        string='Comsumption Units',
        states={'done': [('readonly', True)]})

    consump_percent = fields.Many2many(
        comodel_name='hyd_stock_conso.cons_percent',
        string='Comsumption Percent',
        states={'done': [('readonly', True)]})

    @api.onchange('location_id', 'location_dest_id')
    def _onchange_location_id(self):
        all_unit = self.env['hyd_stock_conso.consumption_unit'].search([])
        all_unit = all_unit.filtered(
            lambda x: self.location_id.id in x.locations_id.ids or 
            self.location_dest_id.id in x.locations_id.ids)
        return {
            'domain':{'consump_units':[('id', 'in', all_unit.ids)]}}

    @api.constrains("state")
    def check_state_for_unit(self):
        # generate unit_line if move.line is done
        for rec in self:
            if rec.state == "done":
                rec.generate_unit_line()

    @api.model
    def generate_unit_line(self):
        unit_line_obj = self.env["hyd_stock_conso.consumption_unit_line"]

        if self.state == "done" and self.consump_units:
            nbre_unit = len(self.consump_units)
            nbre_percent = len(self.consump_percent)

            list_percent = []
            reste_pourcentage = 1.0
            for i in range(nbre_unit):
                if nbre_percent == 0:
                    list_percent.append(1.0/nbre_unit)
                elif nbre_percent == nbre_unit:
                    list_percent.append(self.consump_percent[i].ratio)
                else:
                    if i < nbre_percent:
                        ratio = self.consump_percent[i].ratio
                        list_percent.append(ratio)
                        reste_pourcentage -= ratio
                    else:
                        list_percent.append(reste_pourcentage)
                        reste_pourcentage = 0

            rang = 0
            for unit in self.consump_units:

                # is it a consumption (or a return ?)
                is_c = self.location_dest_id.id in unit.locations_id.ids

                percent = list_percent[rang]
                sign = 1 if is_c else -1
                qte = sign * self.qty_done * percent
                rang += 1

                if self.location_dest_id.id in unit.locations_id.ids and \
                   self.location_id.id in unit.locations_id.ids:
                   # src et dst dans emplacement de l'unite on skippe
                   continue

                unit_line_obj.create({
                    'product_id': self.product_id.id,
                    'date': str(self.move_id.date_expected)[:10],
                    'product_qty': qte,
                    'move_id': self.id,
                    'unit_id': unit.id})
