# -*- coding: utf-8 -*-
{
    'name': 'Sales Product Brand',
    'version': '13.0',
    'author': 'Byootan Tech',
    'category': 'Sales',
    'license': 'AGPL-3',
    'summary': """Add Brand For Sales Analysis Report """,
    'depends': ['brand_products', 'sale_management'],
    'data': [
        'reports/sale_report.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
}
