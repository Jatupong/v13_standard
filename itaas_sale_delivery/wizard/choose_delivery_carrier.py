# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Book)

from odoo import fields, api, models, _


class chooseDeliveryCarrier(models.TransientModel):
    _inherit = 'choose.delivery.carrier'

    district_id = fields.Many2one('res.district', string='District')

    @api.onchange('carrier_id')
    def onchange_carrier(self):
        if self.carrier_id:
            district_ids = self.carrier_id.district_ids.ids
            if district_ids:
                self.district_id = district_ids[0]
            else:
                self.district_id = False
            return {
                'domain': {'district_id': [('id', 'in', district_ids)]},
            }
        else:
            self.district_id = False