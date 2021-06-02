# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _

from odoo.exceptions import AccessError, UserError, ValidationError

class Stock_Picking(models.Model):
    _inherit = 'stock.picking'

    def assign_done_qty(self):
        for picking in self:
            if any(move.product_id.tracking != 'none' for move in picking.move_ids_without_package):
                raise UserError(_(
                    'This update only working for product without tracking by LOT or SN'))
            for move in picking.move_ids_without_package:
                move.update({'quantity_done': move.product_uom_qty})
            picking.update({'state': 'assigned'})

