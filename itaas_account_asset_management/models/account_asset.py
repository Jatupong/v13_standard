# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import odoo.addons.decimal_precision as dp
from odoo import api, fields, models, _
from odoo.tools import float_is_zero, float_compare
from odoo.exceptions import UserError, ValidationError
import math
import re
from datetime import date, timedelta

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

    @api.depends('value_residual','purchase_value','salvage_value')
    def get_depreciated_amount(self):
        for asset in self:
            asset.depreciated_amount = asset.purchase_value - asset.salvage_value - asset.value_residual

    @api.model
    def create(self, vals):
        if not vals.get('purchase_date'):
            vals['purchase_date'] = strToDate(vals.get('acquisition_date'))

        if not vals.get('purchase_value'):
            vals['purchase_value'] = vals.get('original_value')

        res = super(account_asset, self).create(vals)
        ean = generate_ean(str(res.id))
        res.barcode = ean
        return res

    @api.onchange('original_value','salvage_value')
    def _onchange_value(self):
        self._set_value()



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