# -*- coding: utf-8 -*-
from odoo import tools, models, fields, api

class PurchaseReport(models.Model):
    _inherit = 'purchase.report'

    product_brand_id = fields.Many2one(comodel_name='product.brand', string='Brand', readonly=True)

    def _select(self):
        return super(PurchaseReport, self)._select() + " , t.product_brand_id as product_brand_id"

    def _group_by(self):
        return super(PurchaseReport, self)._group_by() + " , t.product_brand_id"
