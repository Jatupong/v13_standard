# Copyright 2017-2020 Forgeflow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).
from odoo import api, fields, models


class PurchaseRequest(models.Model):
    _inherit = "purchase.request"

    def _get_my_department(self):
        employees = self.env.user.employee_ids
        return (
            employees[0].department_id
            if employees
            else self.env["hr.department"] or False
        )

    employee_id = fields.Many2one("hr.employee", "Employee")
    department_id = fields.Many2one(
        "hr.department", "Department", default=_get_my_department
    )

    @api.onchange("requested_by")
    def onchange_requested_by(self):
        employees = self.requested_by.employee_ids
        self.employee_id = (
            employees[0].id
            if employees
            else self.env["hr.employee"] or False
        )
        self.department_id = (
            employees[0].department_id
            if employees
            else self.env["hr.department"] or False
        )

    @api.onchange("employee_id")
    def onchange_employee_id(self):
        if self.employee_id:
            self.department_id = self.employee_id.department_id.id


class PurchaseRequestLine(models.Model):
    _inherit = "purchase.request.line"

    department_id = fields.Many2one(
        comodel_name="hr.department",
        related="request_id.department_id",
        store=True,
        string="Department",
        readonly=True,
    )
