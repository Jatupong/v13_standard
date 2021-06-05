# -*- coding: utf-8 -*-
# by itaas.

import odoo.addons.decimal_precision as dp
from odoo import api, fields, models, _
from odoo.tools import float_is_zero, float_compare
from odoo.exceptions import UserError, ValidationError
import math
import re
from datetime import date, timedelta
import calendar
from dateutil.relativedelta import relativedelta
from math import copysign

def strToDate(dt):
    return date(int(dt[0:4]), int(dt[5:7]), int(dt[8:10]))

class account_asset(models.Model):
    _inherit = 'account.asset'

    purchase_value = fields.Float(string='Purchase Value')
    purchase_date = fields.Date(string='Purchase Date')

    barcode = fields.Char(string='Barcode', copy=False, readonly=True, states={'draft': [('readonly', False)]})
    employee_id = fields.Many2one('hr.employee', string='Employee', readonly=True,
                                   states={'draft': [('readonly', False)]})
    department_id = fields.Many2one('hr.department', string='Department', readonly=True,
                                   states={'draft': [('readonly', False)]})
    serial_number = fields.Char(string='Serial Number', readonly=True, states={'draft': [('readonly', False)]})
    note = fields.Text(string='Note')
    depreciated_amount = fields.Float(string='Depreciated Value', readonly=True, compute='get_depreciated_amount')
    asset_disposal_date = fields.Date(string='Disposal Date', readonly=True,
                                      states={'draft': [('readonly', False)], 'open': [('readonly', False)]})

    default_salvage_value = fields.Float(string='Default Salvage Value')

    @api.depends('value_residual','purchase_value','salvage_value')
    def get_depreciated_amount(self):
        for asset in self:
            asset.depreciated_amount = asset.purchase_value - asset.salvage_value - asset.value_residual

    @api.model
    def create(self, vals):
        if not vals.get('purchase_date') and vals.get('acquisition_date'):
            vals['purchase_date'] = strToDate(vals.get('acquisition_date'))

        if not vals.get('purchase_value') and vals.get('original_value'):
            vals['purchase_value'] = vals.get('original_value')

        res = super(account_asset, self).create(vals)
        ean = generate_ean(str(res.id))
        res.barcode = ean
        return res

    @api.onchange('original_value','salvage_value')
    def _onchange_value(self):
        self._set_value()

    @api.onchange('model_id')
    def _onchange_model_id(self):
        super(account_asset, self)._onchange_model_id()
        model = self.model_id
        if model:
            self.salvage_value = model.default_salvage_value


    def _compute_board_amount(self, computation_sequence, residual_amount, total_amount_to_depr, max_depreciation_nb, starting_sequence, depreciation_date):
        amount = 0
        if computation_sequence == max_depreciation_nb:
            # last depreciation always takes the asset residual amount
            amount = residual_amount
        else:
            if self.method in ('degressive', 'degressive_then_linear'):
                amount = residual_amount * self.method_progress_factor
            if self.method in ('linear', 'degressive_then_linear'):
                nb_depreciation = max_depreciation_nb - starting_sequence
                if self.prorata:
                    nb_depreciation -= 1

                month_days = calendar.monthrange(depreciation_date.year, depreciation_date.month)[1]
                if int(self.method_period) % 12 != 0: ###This is month, self.method_period =1 if self.method_period == 12, then per year.
                    number_of_year = self.method_number / 12
                    per_year_depreciation = total_amount_to_depr / number_of_year
                    total_days = (depreciation_date.year % 4) and 365 or 366
                    per_day_depreciation = per_year_depreciation / total_days
                    amount_depreciation = per_day_depreciation * month_days
                    # print('_compute_board_amount----------------------')
                    # print (depreciation_date)
                    # print(number_of_year)
                    # print(per_year_depreciation)
                    # print(total_days)
                    # print(per_day_depreciation)
                    # print(amount_depreciation)

                else: # this is per year
                    amount_depreciation = total_amount_to_depr / nb_depreciation

                linear_amount = min(amount_depreciation, residual_amount)
                print (linear_amount)

                if self.method == 'degressive_then_linear':
                    amount = max(linear_amount, amount)
                else:
                    amount = linear_amount
        return amount

def ean_checksum(eancode):
    """returns the checksum of an ean string of length 13, returns -1 if
    the string has the wrong length"""
    if len(eancode) != 13:
        return -1
    oddsum = 0
    evensum = 0
    eanvalue = eancode
    reversevalue = eanvalue[::-1]
    finalean = reversevalue[1:]

    for i in range(len(finalean)):
        if i % 2 == 0:
            oddsum += int(finalean[i])
        else:
            evensum += int(finalean[i])
    total = (oddsum * 3) + evensum

    check = int(10 - math.ceil(total % 10.0)) % 10
    return check


def check_ean(eancode):
    """returns True if eancode is a valid ean13 string, or null"""
    if not eancode:
        return True
    if len(eancode) != 13:
        return False
    try:
        int(eancode)
    except:
        return False
    return ean_checksum(eancode) == int(eancode[-1])


def generate_ean(ean):
    """Creates and returns a valid ean13 from an invalid one"""
    if not ean:
        return "0000000000000"
    ean = re.sub("[A-Za-z]", "0", ean)
    ean = re.sub("[^0-9]", "", ean)
    ean = ean[:13]
    if len(ean) < 13:
        ean = ean + '0' * (13 - len(ean))
    return ean[:-1] + str(ean_checksum(ean))