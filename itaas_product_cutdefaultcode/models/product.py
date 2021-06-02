# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today  itaas.co.th

from bahttext import bahttext
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime,timedelta,date
from dateutil.relativedelta import relativedelta
import locale
import time
from odoo import api,fields, models
from odoo.osv import osv
# from odoo.report import report_sxw
from odoo.tools import float_compare, float_is_zero


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _get_partner_ref(self):
        for supplier_info in self.seller_ids:
            if supplier_info.name.id == self._context.get('partner_id'):
                product_name = supplier_info.product_name or self.name
                partner_ref = product_name
                break
        else:
            partner_ref = self.name

        return partner_ref

    def get_product_multiline_description_sale(self):
        """ Compute a multiline description of this product, in the context of sales
                (do not use for purchases or other display reasons that don't intend to use "description_sale").
            It will often be used as the default description of a sale order line referencing this product.
        """
        name = self._get_partner_ref()
        if self.description_sale:
            name += '\n' + self.description_sale

        return name