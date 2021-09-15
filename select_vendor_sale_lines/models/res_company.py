# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class ResCompany(models.Model):
    _inherit = "res.company"

    supplier_id = fields.Many2one('product.supplierinfo')
    use_supplier_per_line = fields.Boolean()