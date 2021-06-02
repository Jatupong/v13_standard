# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo import models, fields, api, _


class ResUsersInherit(models.Model):
    _inherit = 'res.users'
    
    sh_pricelist_ids = fields.Many2many('product.pricelist', 'res_users_product_pricelist_rel', string='Price List')

        
class PricelistInherit(models.Model):
    _inherit = 'product.pricelist'
 
    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        
        if self.env.user.sh_pricelist_ids.ids:
            args.append(('id', 'in', self.env.user.sh_pricelist_ids.ids))
 
        res = super(PricelistInherit, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
        if self.env.user.sh_pricelist_ids:
            return self.env.user.sh_pricelist_ids.ids
        else:
            return res

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.depends('country_id')
    @api.depends_context('force_company')
    def _compute_product_pricelist(self):
        # print('def _compute_product_pricelist')
        company = self.env.context.get('force_company', False)
        res = self.env['product.pricelist']._get_partner_pricelist_multi(self.ids, company_id=company)
        # print('res : ', res)
        for p in self:
            if res.get(p.id) and len(res.get(p.id)) > 1:
                # print('res.get(p.id) : ', res.get(p.id))
                property_product_pricelist = res.get(p.id)
                p.property_product_pricelist = property_product_pricelist[0]
            else:
                p.property_product_pricelist = res.get(p.id)
