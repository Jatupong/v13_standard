# -*- coding: utf-8 -*-
# ©  2015-2020 Deltatech
# See README.rst file on addons root folder for license details


from odoo import api, models, fields, _
from odoo.exceptions import except_orm, Warning, RedirectWarning, UserError


# todo: nu e mai bine sa folosesc un wizard deja existent : choose.delivery.package

class DeliveryCarrierDetails(models.TransientModel):
    _name = 'delivery.carrier.details'
    _description = "Delivery Carrier Details"

    picking_id = fields.Many2one('stock.picking', readonly=True)
    carrier_id = fields.Many2one('delivery.carrier', string='Carrier', related='picking_id.carrier_id', readonly=False,
                                 required=True)

    # Delivery Address
    partner_id = fields.Many2one('res.partner', string='Delivery Address', related='picking_id.partner_id',
                                 readonly=True)

    country_id = fields.Many2one('res.country', string='Country', related='partner_id.country_id', readonly=False)
    state_id = fields.Many2one('res.country.state', string='State', related='partner_id.state_id', readonly=False,
                               domain="[('country_id', '=?', country_id)]", required=True)
    city_id = fields.Many2one('res.city', string='City', related='partner_id.city_id',
                              domain="[('state_id', '=?', state_id)]", required=True,
                              readonly=False)
    city = fields.Char(string='City Name', related='partner_id.city', readonly=False)
    street = fields.Char(string='Street', related='partner_id.street', readonly=False, required=True)
    street2 = fields.Char(string='Street 2', related='partner_id.street2', readonly=False)
    zip = fields.Char(string='ZIP', related='partner_id.zip', readonly=False)
    phone = fields.Char(related='partner_id.phone', readonly=False)

    invoice_id = fields.Many2one('account.move')  # este necesar ca sa fie completat in AWB nur de factura ?

    origin = fields.Char(string='Origin', related='picking_id.origin', readonly=False)
    number_of_parcels = fields.Integer(default=1, related=False, readonly=False, required=True)
    parcel_value = fields.Monetary(related=False, readonly=False)
    value_to_collect = fields.Monetary(related=False, readonly=False)
    currency_id = fields.Many2one('res.currency', related='picking_id.currency_id', readonly=False)

    total_weight = fields.Float(string='TotalWeight', related='picking_id.total_weight', readonly=False)
    weight_uom_name = fields.Char(string='Weight unit of measure label', compute='_compute_weight_uom_name')

    @api.onchange('zip')
    def onchange_zip(self):
        if self.zip:
            city = self.env['res.city'].search([('zipcode', '=', self.zip)])
            if len(city) == 1:
                self.city_id = city
                self.state_id = city.state_id

    @api.onchange('city_id')
    def onchange_city_id(self):
        if self.city_id:
            self.city = self.city_id.name
            if self.city_id.zipcode:
                self.zip = self.city_id.zipcode

    def _compute_weight_uom_name(self):
        weight_uom_id = self.env['product.template']._get_weight_uom_id_from_ir_config_parameter()
        for item in self:
            item.weight_uom_name = weight_uom_id.name

    @api.model
    def default_get(self, fields_list):
        defaults = super(DeliveryCarrierDetails, self).default_get(fields_list)

        active_id = self.env.context.get('active_id', False)
        if not active_id:
            raise UserError(_('Please select a delivery'))
        delivery = self.env['stock.picking'].browse(active_id)
        defaults['picking_id'] = delivery.id
        defaults['carrier_id'] = delivery.carrier_id.id

        address = delivery.partner_id

        if not address.country_id:
            address.country_id = self.env.user.company_id.partner_id.country_id

        # Nu trebuie modificata adresa
        # if not address.city_id and address.city:
        #     domain = [('name', '=', address.city)]
        #     if address.state_id:
        #         domain += [('state_id', '=', address.state_id.id)]
        #     city = self.env['res.city'].search(domain)
        #     if city and len(city) == 1:
        #         address.write({'city_id': city.id, 'state_id': city.state_id.id})

        # care este comanda de vanzare pentru acest picking ?
        # se presupune ca livrarea este completa !

        if delivery.value_to_collect:
            value_to_collect = delivery.value_to_collect
        else:
            value_to_collect = 0
            tx = delivery.sale_id.sudo().transaction_ids.get_last_transaction()
            if tx and tx.acquirer_id == delivery.carrier_id.payment_on_delivery_id:
                value_to_collect = delivery.sale_id.amount_total

        defaults['parcel_value'] = delivery.sale_id.amount_total
        defaults['value_to_collect'] = value_to_collect
        defaults['currency_id'] = delivery.sale_id.currency_id.id  # todo: de convertit valoarea in moneda companiei
        defaults['number_of_parcels'] = delivery.number_of_parcels
        return defaults

    def do_save(self):

        self.picking_id.write({
            'carrier_ready': True,
            'parcel_value': self.parcel_value,
            'value_to_collect': self.value_to_collect,
            'number_of_parcels': self.number_of_parcels
        })
