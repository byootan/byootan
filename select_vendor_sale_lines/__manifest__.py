# -*- coding: utf-8 -*-
{
    'name': 'Select Vendor On SO Lines',
    'version': '13.0',
    'author': 'Byootan Tech',
    'category': 'Operations/Inventory',
    'license': 'AGPL-3',
    'summary': """Add Supplier IN SO lines """,
    'depends': ['sale_stock', 'purchase_stock', 'sales_team'],
    'data': [
        'views/sale_order_lines.xml',
        'views/res_config_settings_view.xml',
        'security/security.xml',
    ],
    # 'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
    'application': False,

}
