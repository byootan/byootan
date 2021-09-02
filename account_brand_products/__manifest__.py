# -*- coding: utf-8 -*-
{
    'name': 'Account Product Brand',
    'version': '13.0',
    'author': 'Byootan Tech',
    'category': 'Product Management',
    'license': 'AGPL-3',
    'summary': """Add Brand For Account Analysis Report """,
    'depends': ['brand_products', 'account'],
    'data': [
        'reports/account_invoice_report_view.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
}
