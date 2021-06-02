# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS

from odoo import api,fields, models

class ProjectTask(models.Model):
    _inherit = 'project.task'

    employee_ids = fields.Many2many('hr.employee',string="Employee" )

