# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json

from odoo import models, fields, api, _
from odoo.exceptions import UserError

import unicodedata


class DeliveryService(models.Model):
    _name = 'delivery.carrier.service'
    _description = 'Carrier Service'

    code = fields.Char()
    name = fields.Char()
    delivery_type = fields.Selection([('fixed', 'Fixed Price')])


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    update_address = fields.Boolean("Update address dictionaries")
    company_partner_id = fields.Many2one('res.partner', compute='_compute_partner')
    service_id = fields.Many2one('delivery.carrier.service', domain="[('delivery_type','=',delivery_type)]")

    payment_on_delivery_id = fields.Many2one('payment.acquirer', string='Payment On Delivery')

    username = fields.Char(string="User", groups="base.group_system")
    password = fields.Char(string="Password", groups="base.group_system")
    pickup_location_id = fields.Many2one('res.partner', string='Pickup Location',
                                         domain="[('type','=','delivery'),('parent_id','=',company_partner_id)]")

    def action_init_carrier(self):
        self.ensure_one()
        if hasattr(self, '%s_init_carrier' % self.delivery_type):
            return getattr(self, '%s_init_carrier' % self.delivery_type)()

    def action_import_carrier_city(self):
        self.ensure_one()
        if hasattr(self, '%s_import_carrier_city' % self.delivery_type):
            return getattr(self, '%s_import_carrier_city' % self.delivery_type)()
        self.write({'update_address': False})

    def _compute_partner(self):
        for delivery in self:
            company = delivery.company_id or self.env.company
            delivery.company_partner_id = company.partner_id

    def strip_accents(self, text):
        text = unicodedata.normalize('NFD', text or '').encode('ascii', 'ignore').decode("utf-8")
        return str(text)

    def get_ship_from(self):
        ship_from = {
            'ref': self.pickup_location_id.ref,
            'partner': self.pickup_location_id.name,
            'phone': self.pickup_location_id.phone,
            'city': self.strip_accents(self.pickup_location_id.city),
            'region': self.strip_accents(self.pickup_location_id.state_id.name),
            'zip': self.pickup_location_id.zip,
            'street': self.pickup_location_id.street or '',
            'email': self.pickup_location_id.email,
        }
        return ship_from

    def get_order_delivery_details(self, order):

        if not order.partner_shipping_id.city_id:
            domain = []
            if order.partner_shipping_id.state_id:
                domain += [('state_id', '=', order.partner_shipping_id.state_id.id)]
            if order.partner_shipping_id.zip:
                domain += [('zipcode', '=', order.partner_shipping_id.zip)]
            else:
                domain += [('name', '=ilike', order.partner_shipping_id.city)]
            city = self.env['res.city'].sudo().search(domain)

            if city and len(city) == 1:
                order.partner_shipping_id.write({'city_id': city.id})

        total_qty = 0.0
        total_weight = 0.0
        for line in order.order_line.filtered(lambda l: not l.is_delivery):
            total_qty += line.product_uom_qty
            total_weight += line.product_id.weight * line.product_qty

        value_to_collect = 0.0
        tx = order.sudo().transaction_ids.get_last_transaction()
        if tx and tx.acquirer_id == self.payment_on_delivery_id:
            value_to_collect = order.amount_total

        ship_to = {
            'partner': order.partner_shipping_id.name,
            'is_company': order.partner_shipping_id.is_company,
            'vat': order.partner_shipping_id.vat,
            'phone': order.partner_shipping_id.phone,

            'city': self.strip_accents(order.partner_shipping_id.city),
            'region': self.strip_accents(order.partner_shipping_id.state_id.name),
            'zip': order.partner_shipping_id.zip,
            'street': order.partner_shipping_id.street or '',
            'street2': order.partner_shipping_id.street2 or '',
            'email': order.partner_shipping_id.email or '',
        }

        shipment_info = {
            'number_of_parcels': 1,
            'total_qty': total_qty,
            'total_weight': total_weight,
            'parcel_value': order.amount_total,
            'value_to_collect': value_to_collect,
            'note': order.note or '',
            'custom': order.name,
            'origin': order.reference or '',
            'service': self.service_id.code,
            'ship_to': ship_to,
            'pickup_point': self.pickup_location_id.ref
        }
        shipment_info.update(ship_to)  # todo: de eliminat
        return shipment_info

    def get_picking_delivery_details(self, picking):

        ship_to = {
            'partner': picking.partner_id.name,
            'is_company': picking.partner_id.is_company,
            'vat': picking.partner_id.vat,
            'phone': picking.partner_id.phone,

            'city': self.strip_accents(picking.partner_id.city),
            'region': self.strip_accents(picking.partner_id.state_id.name),
            'zip': picking.partner_id.zip,
            'street': picking.partner_id.street or '',
            'street2': picking.partner_id.street2 or '',
            'email': picking.partner_id.email or '',
        }

        shipment_info = {
            'number_of_parcels': picking.number_of_parcels,
            'total_weight': picking.total_weight,
            'parcel_value': picking.value_to_collect,
            'value_to_collect': picking.value_to_collect,
            'note': picking.note or '',
            'custom': picking.name,
            'origin': picking.origin,
            'service': self.service_id.code,
            'ship_to': ship_to,
            'pickup_point': self.pickup_location_id.ref
        }
        shipment_info.update(ship_to)  # todo: de eliminat
        return shipment_info
