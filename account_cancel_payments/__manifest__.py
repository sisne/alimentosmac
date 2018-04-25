# -*- coding: utf-8 -*-
{
    'name': 'Account Cancel Payments',
    'category': 'Account',
    'description':"""
Allow cancelling Account Payment & Allow to set to draft again. 
""",
    'author': 'SisNe, SRL',
    'website': 'https://sisne.do/',
    'version': '9.1.0',
    'depends': ['account', 'account_cancel'],
    'data' : [
        'views/account_payment_view.xml',
    ],
    'qweb': [],
    'auto_install': False,
    'installable': True,
    'application': True,

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
