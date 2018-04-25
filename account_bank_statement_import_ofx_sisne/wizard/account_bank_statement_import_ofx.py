# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import StringIO
from xml.etree import ElementTree
from datetime import datetime

try:
    from ofxparse import OfxParser
    from ofxparse.ofxparse import OfxParserException
    OfxParserClass = OfxParser
except ImportError:
    logging.getLogger(__name__).warning("The ofxparse python library is not installed, ofx import will not work.")
    OfxParser = OfxParserException = None
    OfxParserClass = object

from odoo import models, _
from odoo.exceptions import UserError
from odoo.addons.account_bank_statement_import_ofx.wizard.account_bank_statement_import_ofx import PatchedOfxParser


class AccountBankStatementImport(models.TransientModel):
    _inherit = 'account.bank.statement.import'

    def _parse_file(self, data_file):
        if not self._check_ofx(data_file):
            return super(AccountBankStatementImport, self)._parse_file(data_file)
        if OfxParser is None:
            raise UserError(_("The library 'ofxparse' is missing, OFX import cannot proceed."))

        ofx = PatchedOfxParser.parse(StringIO.StringIO(data_file))
        vals_bank_statement = []
        account_lst = set()
        currency_lst = set()
        for account in ofx.accounts:
            account_lst.add(account.number)
            currency_lst.add(account.statement.currency)
            transactions = []
            total_amt = 0.00
            for transaction in account.statement.transactions:
                # Since ofxparse doesn't provide account numbers, we'll have to find res.partner and res.partner.bank here
                # (normal behaviour is to provide 'account_number', which the generic module uses to find partner/bank)
                bank_account_id = partner_id = False
                partner_bank = self.env['res.partner.bank'].search([('partner_id.name', '=', transaction.payee)], limit=1)
                if partner_bank:
                    bank_account_id = partner_bank.id
                    partner_id = partner_bank.partner_id.id
                
                current_time = datetime.now().strftime("%m%d%Y%H%M%S")
                vals_line = {
                    'date': transaction.date,
                    'name': transaction.payee + (transaction.memo and ': ' + transaction.memo or ''),
                    'ref': str(transaction.date.strftime("%Y%m%d")) + str(transaction.id.zfill(4)),
                    'amount': transaction.amount,
                    'unique_import_id': str(transaction.date.strftime("%Y%m%d")) + str(transaction.id.zfill(4)),
                    'bank_account_id': bank_account_id,
                    'partner_id': partner_id,
                    'sequence': len(transactions) + 1,
                }
                total_amt += float(transaction.amount)
                transactions.append(vals_line)
            vals_bank_statement.append({
                'transactions': transactions,
                # WARNING: the provided ledger balance is not necessarily the ending balance of the statement
                # see https://github.com/odoo/odoo/issues/3003
                'balance_start': float(account.statement.balance) - total_amt,
                'balance_end_real': account.statement.balance,
            })

        if account_lst and len(account_lst) == 1:
            account_lst = account_lst.pop()
            currency_lst = currency_lst.pop()
        else:
            account_lst = None
            currency_lst = None

        return currency_lst, account_lst, vals_bank_statement
