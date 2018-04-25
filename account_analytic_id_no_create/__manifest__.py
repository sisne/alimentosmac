# -*- coding: utf-8 -*-
{
    'name': 'Account Analytic Id No Create',
    'category': 'Account',
    'description':"""
Do not allow creating analytic accounts on the go. 
""",
    'author': 'SisNe, SRL',
    'website': 'https://sisne.do/',
    'version': '1.0.1',
    'depends': ['account'],
    'data' : [
        'views/account_invoice_view.xml',
    ],
    'qweb': [],
    'auto_install': False,
    'installable': True,
    'application': True,

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
