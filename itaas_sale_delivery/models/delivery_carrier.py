# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Book)

from odoo import fields, api, models, _


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    district_ids = fields.Many2many('res.district', 'delivery_carrier_district_rel', 'carrier_id', 'district_id', 'Districts')