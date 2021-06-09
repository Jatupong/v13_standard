from odoo import models, fields ,api ,_
from odoo.exceptions import UserError


class MaterialPurchaseRequisition(models.Model):
    _inherit = "material.purchase.requisition"

    request_id = fields.Many2one('purchase.request', string="Purchase Request")
    production_id = fields.Many2one('mrp.production', string="Production")
    purchase_id = fields.Many2one('purchase.order', string="Purchase Order")
    repair_id = fields.Many2one('repair.order', string="Repair Order")
    doc_reference = fields.Selection([('pr', 'PR Reference'), ('po', 'PO Reference'),
                                      ('mo', 'MO Reference'), ('repair', 'Repair Reference')],
                                     string='Doc Reference')
    operation_id = fields.Many2one('mrp.routing.workcenter', string="Operation")
    routing_id = fields.Many2one('mrp.routing',related='production_id.routing_id' ,string="Routing")

    def action_product_reference(self):
        context = dict(self._context or {})
        doc = context.get('doc')
        line_list = []

        if doc == 'pr':
            line_ids = self.request_id.line_ids
            for pr in line_ids:
                vals = {
                    'product_id': pr.product_id.id,
                    'description': pr.product_id.name,
                    'qty': pr.product_qty,
                    'uom_id': pr.product_uom_id.id,
                    'origin': pr.name,
                    'requisition_action': 'internal_picking',
                }
                line_list.append((0, 0, vals))
        elif doc == 'po':
            line_ids = self.purchase_id.order_line
            for po in line_ids:
                vals = {
                    'product_id': po.product_id.id,
                    'description': po.product_id.name,
                    'qty': po.product_uom_qty,
                    'uom_id': po.product_uom.id,
                    'origin': po.name,
                    'requisition_action': 'internal_picking',
                }
                line_list.append((0, 0, vals))
        elif doc == 'repair':
            line_ids = self.repair_id.operations
            for re in line_ids:
                vals = {
                    'product_id': re.product_id.id,
                    'description': re.product_id.name,
                    'qty': re.product_uom_qty,
                    'uom_id': re.product_uom.id,
                    'origin': re.name,
                    'requisition_action': 'internal_picking',
                }
                line_list.append((0, 0, vals))
        else:
            if self.operation_id:
                line_ids = self.production_id.move_raw_ids.filtered(lambda r: r.bom_line_id.operation_id == self.operation_id)
            else:
                line_ids = self.production_id.move_raw_ids

            for mo in line_ids:
                product_uom_qty = mo.product_uom_qty - mo.requisition_qty
                if product_uom_qty < 0:
                    product_uom_qty = 0
                vals = {
                    'product_id': mo.product_id.id,
                    'description': mo.product_id.name,
                    'qty': product_uom_qty,
                    'uom_id': mo.product_uom.id,
                    'origin': mo.name,
                    'move_line_id': mo.id,
                    'requisition_action': 'internal_picking',
                }
                line_list.append((0, 0, vals))

        if not line_list:
            raise UserError(_("Hasn't product, document or requisition qty"))
        else:
            self.update({'requisition_line_ids': line_list})

    def create_picking_po(self):
        responsible_by = []
        if self.requisition_line_ids:
            for re_line in self.requisition_line_ids:
                re_line.check_qty_requisition(self.doc_reference, True)
        #     product_ids = self.requisition_line_ids.filtered(
        #         lambda r: r.product_id.categ_id and r.product_id.categ_id.responsible_by).mapped('product_id')
        #     # print('product_ids :',product_ids)
        #     if product_ids:
        #         categ_ids = product_ids.mapped('categ_id')
        #         # print('categ_ids :', categ_ids)
        #         responsible_by = categ_ids.mapped('responsible_by').ids
        #         # print('responsible_by :', responsible_by)
        #
        # if responsible_by and self.env.uid not in responsible_by:
        #     raise UserError(_("Please contact responsible product category."))

        return super(MaterialPurchaseRequisition, self).create_picking_po()

    # def confirm_requisition(self):
    #     if self.requisition_line_ids:
    #         for re_line in self.requisition_line_ids:
    #             re_line.check_qty_requisition(self.doc_reference,re_line.qty, False)
    #
    #     return super(MaterialPurchaseRequisition, self).confirm_requisition()


class Requisition(models.Model):
    _inherit = "requisition.line"

    origin = fields.Char('Source Document', copy=False, help="Reference of the document")
    move_line_id = fields.Many2one('stock.move', string='Stock Move Reference')

    def check_qty_requisition(self, doc_reference, update):
        if doc_reference == 'mo':
            # print('self.qty:',self.qty)
            requisition_qty = self.qty + self.move_line_id.requisition_qty
            # print('qty : ', self.qty)
            # print('mo requisition_qty : ', self.move_line_id.requisition_qty)
            # print('mo product_uom_qty : ', self.move_line_id.product_uom_qty)
            # print('requisition_qty : ', requisition_qty)
            self.move_line_id.update({'requisition_qty': requisition_qty,
                                      })

        # if requisition_qty <= self.move_line_id.product_uom_qty:
        #     if update:
        #         self.move_line_id.update({'requisition_qty': requisition_qty})
        # else:
        #     raise UserError(_('Requisition more than Qty. %s.') % self.product_id.display_name)