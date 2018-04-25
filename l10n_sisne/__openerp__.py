# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Dominican Republic - Accounting',
    'version': '1.0',
    'category': 'Localization',
    'description': """
This is a base module to manage the accounting for Dominican Republic.
======================================================================

* The main taxes used in Domincan Republic
* Fiscal position for local """,
    
    'author': 'SISNE, SRL.',
    'website': 'http://sisne.do',
    'depends': ['account', 'base_iban'],
    'data': [

        'data/account_chart_template.xml',
        'data/account_tax_template.xml',
        'data/account_fiscal_position_template.xml',
        'data/account_fiscal_position_tax_template.xml',
        'data/l10n_do_base_data.xml',
        'data/account_chart_template.yml'

    ],
    
    'test': [],
    'demo': [],
    'installable': True,
    'auto_install': False,
}