# -*- coding: utf-8 -*-
# Copyright (c) 2015-Present TidyWay Software Solution. (<https://tidyway.in/>)

from odoo import models, api, _
from odoo.exceptions import Warning


class GeneratePo(models.TransientModel):
    _name = 'generate.po'
    _description = 'Generate Purchase Order'

    @api.model
    def _check_warnings(self, tender_ids, tender_states):
        if not tender_ids:
            raise Warning(_('You are only generate purchase order for tender.'))
        if len(tender_ids) > 1:
            raise Warning(_('Selected lines must be from same tender.'))
        if len(tender_states) > 1:
            raise Warning(_('Selected lines tender must be on "Bid Selection" State.'))
        if 'open' not in tender_states:
            raise Warning(_('Selected lines Tender must be on "Bid Selection" State.'))


    def generate_po(self):
        """
            Generate Purchase Order
        """
        pol_obj = self.env['purchase.order.line']
        req_obj = self.env['purchase.requisition']
        ctx = dict(self._context or {})
        line_ids = ctx.get('active_ids', []) or []
        tender_ids = []
        tender_states = []
        for line in pol_obj.browse(line_ids):
            if line.order_id and line.order_id.requisition_id:
                tender_ids.append(line.order_id.requisition_id.id)
                tender_states.append(line.order_id.requisition_id.state)
        tender_ids = list(set(tender_ids))
        if len(tender_ids) > 1:
            raise Warning(_('You should select only single tender lines'))
        tender_states = list(set(tender_states))
        self._check_warnings(tender_ids, tender_states)
        tenders = req_obj.browse(tender_ids)
        return tenders.generate_po()
