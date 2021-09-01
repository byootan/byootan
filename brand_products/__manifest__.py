# -*- coding: utf-8 -*-
{
    'name': 'Product Brand',
    'version': '13.0',
    'author': 'Byootan Tech',
    'category': 'Product Management',
    'license': 'AGPL-3',
    'summary': """Add Brand For Products """,
    'depends': ['base','sale','purchase'
    ],
    'data': [
        'views/product_product.xml',
        'views/product_template.xml',
        'views/product_brand.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,

}
