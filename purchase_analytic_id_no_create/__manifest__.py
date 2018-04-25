# -*- coding: utf-8 -*-
{
    'name': 'Purchase Analytic Id No Create',
    'category': 'Purchase',
    'description':"""
Do not allow creating analytic accounts on the go. 
""",
    'author': 'SisNe, SRL',
    'website': 'https://sisne.do/',
    'version': '1.0.1',
    'depends': ['account'],
    'data' : [
        'views/purchase_views.xml',
    ],
    'qweb': [],
    'auto_install': False,
    'installable': True,
    'application': True,

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
