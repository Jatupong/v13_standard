# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _

from odoo.exceptions import AccessError, UserError, ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    ##T20094072,T20094075##
    is_test = fields.Boolean(string='Is Test') ##############JA-20/09/2020, this will be a flag to let system not create a sequence

    @api.model
    def create(self, vals):
        ############if we add some value to vals['name'] then system will not consider to run sequence anymore.
        ############This is test then assign some value
        if 'is_test' in vals:
            vals['name'] = 'Test'

        else:
            ####### This is real so assign the value with proper sequence date
            ####### with_context(ir_sequence_date=vals['date_order']), this parameter is the key of make system running with correct date
            if 'date_order' in vals:
                seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date_order']))
                if 'company_id' in vals:
                    vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id'],ir_sequence_date=vals['date_order']).next_by_code(
                        'sale.order', sequence_date=seq_date) or _('New')
                else:
                    vals['name'] = self.env['ir.sequence'].with_context(
                        ir_sequence_date=vals['date_order']).next_by_code('sale.order', sequence_date=seq_date) or _(
                        'New')

        return super(SaleOrder, self).create(vals)
