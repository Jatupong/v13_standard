# © 2016 OdooMRP team
# © 2016 AvanzOSC
# © 2016 Serv. Tecnol. Avanzados - Pedro M. Baeza
# © 2016 ForgeFlow S.L. (https://forgeflow.com)
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, models
from datetime import datetime, timedelta
from functools import partial
from itertools import groupby

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare


class SaleOrder(models.Model):
    _inherit = "sale.order"
    # origin = fields.Char(string='Paid amount', help="Reference of the document that generated this sales order request.")
    period_payment_amount = fields.Float(string='Payment Amount')
    period = fields.Char(string='Invoice Period')

    def _get_invoice_grouping_keys(self):
        return ['company_id', 'invoice_origin', 'currency_id']


    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        if self.period:
            res['period'] = self.period
        if self.period_payment_amount:
            res['period_payment_amount'] = self.period_payment_amount

        return res

