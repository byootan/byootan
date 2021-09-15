# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    supplier_id = fields.Many2one(related='company_id.supplier_id', string="Supplier", readonly=False)
    use_supplier_per_line = fields.Boolean(related='company_id.use_supplier_per_line', readonly=False)