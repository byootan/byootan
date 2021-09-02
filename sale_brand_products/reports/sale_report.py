# -*- coding: utf-8 -*-
from odoo import tools, models, fields, api


class SaleReport(models.Model):
    _inherit = 'sale.report'

    product_brand_id = fields.Many2one(
        comodel_name='product.brand',
        string='Brand', readonly=True)

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['product_brand_id'] = ", t.product_brand_id as product_brand_id"
        groupby += " , t.product_brand_id"
        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)
