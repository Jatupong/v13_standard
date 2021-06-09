# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Book)

from odoo import fields, api, models, _
from odoo.exceptions import UserError, AccessError


class SalePicking(models.Model):
    _inherit = "stock.picking"

    is_validate_delivered = fields.Boolean(string='Delivery Validate', related='sale_id.is_validate_delivered')

    def button_validate(self):
        for obj in self:
            if obj.sale_id and not obj.is_validate_delivered:
                raise UserError(_('Not Delivery Validate.'))

        return super(SalePicking, self).button_validate()