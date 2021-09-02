# -*- coding: utf-8 -*-
from odoo import tools, models, fields, api


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    product_brand_id = fields.Many2one(comodel_name="product.brand", string="Brand")

    @api.model
    def _select(self):
        select_str = super(AccountInvoiceReport, self)._select()
        select_str += """
            , template.product_brand_id as product_brand_id
            """
        return select_str

    @api.model
    def _group_by(self):
        group_by_str = super(AccountInvoiceReport, self)._group_by()
        group_by_str += ", template.product_brand_id"
        return group_by_str
