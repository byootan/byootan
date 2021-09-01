# -*- coding: utf-8 -*-
from odoo import api, fields, models

class SimpleProductBrand(models.Model):
    _name = 'product.brand'
    _description = 'Product Brand'

    active = fields.Boolean(default=True)
    name = fields.Char(string='Brand Name', required=True, translate=True)
    description = fields.Text(string='Description', translate=True)
    image = fields.Binary(string='Logo')
    brand_products = fields.One2many(
        'product.template',
        'product_brand_id',
        string='Related Products',)
    brand_products_count = fields.Integer(string='#Products',compute='_compute_brand_product_count')

    @api.depends('brand_products')
    def _compute_brand_product_count(self):
        self.brand_products_count = len(self.brand_products)


