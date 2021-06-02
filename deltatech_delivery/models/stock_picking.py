# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json

from odoo import models, fields, api, _
from odoo.exceptions import UserError



class StockPicking(models.Model):
    _inherit = 'stock.picking'

    carrier_ready = fields.Boolean()
    # campui necesare: nr de colete, valoare colete, suma de coletat, nr de factura !

    total_weight = fields.Float(default=1)
    number_of_parcels = fields.Integer(default=1)
    parcel_value = fields.Monetary()
    value_to_collect = fields.Monetary()
    currency_id = fields.Many2one('res.currency')


    def put_in_pack(self):
        res = super(StockPicking, self).put_in_pack()
        return  res



    def carrier_details(self):
        action = self.env.ref('deltatech_delivery.action_delivery_carrier_details').read()[0]
        return action


    def send_to_shipper(self):
        if self.carrier_ready:
            return super(StockPicking, self).send_to_shipper()
        else:
            return self.carrier_details()






