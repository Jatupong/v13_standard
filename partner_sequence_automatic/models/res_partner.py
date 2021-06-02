# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = "res.partner"
    _description = "Res partner Sequences"

    partner_type = fields.Selection([('customer', 'Customer'),
                                     ('vendor', 'Vendor'),
                                     ('both', 'Customer & Vendor'),
                                     ('other', 'Other'),
                                     ],string="Partner Type", tracking=True)

    @api.model
    def create(self, vals):
        if ('ref' not in vals or not vals['ref']):
            if 'partner_type' in vals:
                if vals['partner_type'] == 'customer':
                    ref = self.env['ir.sequence'].next_by_code('res.partner.customer') or '/'
                elif vals['partner_type'] == 'vendor':
                    ref = self.env['ir.sequence'].next_by_code('res.partner.vendor') or '/'
                else:
                    ref = self.env['ir.sequence'].next_by_code('res.partner') or '/'
            else:
                if 'customer_rank' in vals or 'supplier_rank' in vals:
                    if vals['customer_rank'] == 1 and vals['supplier_rank'] == 0:
                        vals['partner_type'] = 'customer'
                        ref = self.env['ir.sequence'].next_by_code('res.partner.customer') or '/'
                    elif vals['customer_rank'] == 0 and vals['supplier_rank'] == 1:
                        vals['partner_type'] = 'vendor'
                        ref = self.env['ir.sequence'].next_by_code('res.partner.vendor') or '/'
                    else:
                        vals['partner_type'] = 'other'
                        ref = self.env['ir.sequence'].next_by_code('res.partner') or '/'
                else:
                    vals['partner_type'] = 'other'
                    ref = self.env['ir.sequence'].next_by_code('res.partner') or '/'

            vals['ref'] = ref

        return super(ResPartner, self).create(vals)

    @api.onchange('partner_type')
    def onchange_partner_type(self):
        if self.partner_type == 'customer':
            self.customer_rank = 1
            self.supplier_rank = 0
        elif self.partner_type == 'vendor':
            self.customer_rank = 0
            self.supplier_rank = 1
        elif self.partner_type == 'both':
            self.customer_rank = 1
            self.supplier_rank = 1
        else:
            self.customer_rank = 0
            self.supplier_rank = 0

    @api.model
    def default_get(self, fields_list):
        defaults = super(ResPartner, self).default_get(fields_list)
        search_partner_mode = self.env.context.get('res_partner_search_mode')
        print('search_partner_mode : ',search_partner_mode)
        is_customer = search_partner_mode == 'customer'
        is_supplier = search_partner_mode == 'supplier'

        if is_customer and is_supplier:
            partner_type = 'both'
        elif is_customer and not is_supplier:
            partner_type = 'customer'
        elif not is_customer and is_supplier:
            partner_type = 'vendor'
        else:
            partner_type = 'other'

        defaults.update({'partner_type': partner_type})
        print('defaults : ',defaults)
        return defaults

    def set_partner_type(self):
        partner_ids = self.env['res.partner'].search([('parent_id','=',False),
                                                      ('partner_type','=',False)
                                                      ])
        for obj in partner_ids:
            is_customer = obj.customer_rank > 0
            is_supplier = obj.supplier_rank > 0
            if is_customer and is_supplier:
                partner_type = 'both'
            elif is_customer and not is_supplier:
                partner_type = 'customer'
            elif not is_customer and is_supplier:
                partner_type = 'vendor'
            else:
                partner_type = 'other'

            obj.update({'partner_type':partner_type})


    # @api.model_create_multi
    # def create(self, vals_list):
    #     search_partner_mode = self.env.context.get('res_partner_search_mode')
    #     is_customer = search_partner_mode == 'customer'
    #     is_supplier = search_partner_mode == 'supplier'
    #     if search_partner_mode:
    #         for vals in vals_list:
    #             if is_customer and 'customer_rank' not in vals:
    #                 vals['customer_rank'] = 1
    #             elif is_supplier and 'supplier_rank' not in vals:
    #                 vals['supplier_rank'] = 1
    #     return super().create(vals_list)
