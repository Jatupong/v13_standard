# Powered by SCRIMO GmbH
# -*- coding: utf-8 -*-
# © 2020 SCRIMO GmbH (<http://www.scrimo.com>)

from odoo import api, fields, models, SUPERUSER_ID, _
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

class SCBirthdayResPartner(models.Model):
    _inherit = 'res.partner'

    sc_birthdate = fields.Date(string='Date of Birth', )
    sc_age = fields.Integer(compute='_compute_sc_age', string='Age')
    sc_under_18 = fields.Boolean(compute="_compute_sc_age", string='Under 18', store=True)

    @api.depends('sc_birthdate')
    def _compute_sc_age(self):
        for rec in self:
            if rec.sc_birthdate:
                d1 = rec.sc_birthdate
                d2 = date.today()
                rec.sc_age = relativedelta(d2, d1).years
                rec.sc_under_18 = bool(relativedelta(d2, d1).years < 18)
            else:
                rec.sc_age = 0
                rec.sc_under_18 = False
