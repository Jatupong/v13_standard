import odoo.addons.decimal_precision as dp
from odoo import models, fields, api, _
from odoo.addons.sale_stock.models.sale_order import SaleOrderLine
from odoo.exceptions import Warning, ValidationError, UserError



class AccountMoveInherit(models.Model):
	_inherit = "account.move"

	pricelist_id = fields.Many2one('product.pricelist' ,string="Pricelist")

	def product_price_update(self):
		for lines in self.invoice_line_ids.filtered(lambda l: l.product_id and l.price_unit > 0.00):
			pricelist_item = self.pricelist_id.item_ids.filtered(
				lambda l: l.compute_price == 'fixed' and l.applied_on == '1_product' and l.uom_id.id == lines.uom_id.id)
			if pricelist_item:
				each_price = self.pricelist_id.item_ids.search([('product_tmpl_id', '=', lines.product_id.product_tmpl_id.id),
																('compute_price', '=', 'fixed'),
																('applied_on', '=', '1_product'),
																('pricelist_id', '=', self.pricelist_id.id),
																('uom_id','=',lines.uom_id.id)])
				if not each_price:
					self.pricelist_id.write({'item_ids': [(0, 0, {'applied_on': '1_product',
																  'product_id': lines.product_id.product_tmpl_id.id,
																  'uom_id' : lines.uom_id.id,
																  'fixed_price': lines.price_unit})]})
				else:
						each_price.fixed_price = lines.price_unit
						
			else:
				self.pricelist_id.write({'item_ids': [(0, 0, {'applied_on': '1_product',
															  'product_id': lines.product_id.product_tmpl_id.id,
															  'uom_id' : lines.uom_id.id,
															  'fixed_price': lines.price_unit
															  })]})



class AccountMoveLineInherit(models.Model):
	_inherit = 'account.move.line'


	@api.onchange('product_id')
	def _onchange_product_id(self):
		domain = {}
		if not self.move_id:
			return

		part = self.move_id.partner_id
		fpos = self.move_id.fiscal_position_id
		company = self.move_id.company_id
		currency = self.move_id.currency_id
		type = self.move_id.type

		if not part:
			warning = {
					'title': _('Warning!'),
					'message': _('You must first select a partner!'),
				}
			return {'warning': warning}

		if not self.product_id:
			if type not in ('in_invoice', 'in_refund'):
				self.price_unit = 0.0
			domain['uom_id'] = []
		else:
			if part.lang:
				product = self.product_id.with_context(lang=part.lang)
			else:
				product = self.product_id

			self.name = product.partner_ref
			account = self._get_computed_account()
			if account:
				self.account_id = account.id
			self._get_computed_taxes()

			if type in ('in_invoice', 'in_refund'):
				if product.description_purchase:
					self.name += '\n' + product.description_purchase
			else:
				if product.description_sale:
					self.name += '\n' + product.description_sale

			if not self.product_uom_id or product.uom_po_id.category_id.id != self.product_uom_id.category_id.id:
				self.uom_id = product.uom_po_id.id
			domain['uom_id'] = [('category_id', '=', product.uom_id.category_id.id)]

			if company and currency:

				if self.product_uom_id and self.product_uom_id != product.uom_po_id.id:
					self.price_unit = product.uom_po_id._compute_price(self.price_unit, self.product_uom_id)
		return {'domain': domain}

	@api.onchange('product_uom_id')
	def _onchange_uom_id(self):
		warning = {}
		result = {}
		date = uom_id = False
		if not self.product_uom_id:
			self.price_unit = 0.0
		if self.product_id and self.product_uom_id:
			if self.product_id.uom_po_id.category_id.id != self.product_uom_id.category_id.id:
				warning = {
					'title': _('Warning!'),
					'message': _('The selected unit of measure is not compatible with the unit of measure of the product.'),
				}

				self.uom_id = self.product_id.uom_po_id.id
			if self.product_uom_id:
				price =dict((product_id, res_tuple[0]) for product_id, res_tuple in self.move_id.pricelist_id._compute_price_rule([(self.product_id, self.quantity, self.partner_id)], date=False, uom_id=self.product_uom_id.id).items())
				
				self.price_unit = price.get(self.product_id.id, 0.0)
				if warning:
					result['warning'] = warning
				return result
