# -*- coding: utf-8 -*-

from openerp.osv import osv
from openerp.report import report_sxw
from openerp.tools.translate import _
import math
LINE_FILLER = '*'
INV_LINES_PER_STUB = 9


class amount_to_text:
    """
    Transforma de una cantidad numerica a cantidad en letra
    ej. 200 -> doscientos
    """

    def __init__(self):
        self._n1 = ( "un","dos","tres","cuatro","cinco","seis","siete","ocho",
            "nueve","diez","once","doce","trece","catorce","quince",
            "dieciseis","diecisiete","dieciocho","diecinueve","veinte")

        self._n11 =( "un","dos","tres","cuatro","cinco","seis","siete","ocho","nueve")

        self._n2 = ( "dieci","veinti","treinta","cuarenta","cincuenta","sesenta",
                "setenta","ochenta","noventa")

        self._n3 = ( "ciento","dosc","tresc","cuatroc","quin","seisc",
                "setec","ochoc","novec")
    
    def amount_to_text_cheque(self, nNumero, intermedio="pesos ", sufijo="M. N." ):
        nNumero = round( nNumero , 2)
        strCantEntera = self.amount_to_text(nNumero)
        intCantDecimal = self.extraeDecimales( nNumero )
        if intCantDecimal<=9:
            strCantDecimal="0%d"%(intCantDecimal)
        else:
            strCantDecimal="%d"%(intCantDecimal)
        strCantDecimal += "/100"
        return strCantEntera+' '+intermedio+' '+strCantDecimal+' '+sufijo
    
    def extraeDecimales(self, nNumero, max_digits=2):
        strDecimales = str( round(nNumero%1, 2) ).replace('0.','')
        strDecimales += "0"*max_digits
        strDecimales = strDecimales[0:max_digits]
        return long( strDecimales )
    
    def amount_to_text(self, nNumero, lFemenino=False):
        """
        NOTA: Solo numeros ENTEROS, omite los DECIMALES.
        amount_to_text(nNumero, lFemenino) --> cLiteral
            Convierte el numero a una cadena literal de caracteres
        P.e.:       201     -->   "doscientos uno"
                    1111     -->   "mil ciento once"

            <nNumero>       Numero a convertir
            <lFemenino>     = 'true' si el Literal es femenino
                            P.e.:   201     -->    "doscientas una"
        """
        # Nos aseguramos del tipo de <nNumero>
        # se podria adaptar para usar otros tipos (pe: float)
        nNumero = long(nNumero)
        if nNumero<0:       cRes = "menos "+self._amount_to_text(-nNumero,lFemenino)
        elif nNumero==0:    cRes = "cero"
        else:               cRes = self._amount_to_text(nNumero,lFemenino)
        
        # Excepciones a considerar
        if not lFemenino and nNumero%10 == 1 and nNumero%100!=11:
            cRes += "o"
        #cRes = cRes.upper()
        #cRes = cRes.capitalize()
        return cRes
    
    # Funcion auxiliar recursiva
    def _amount_to_text(self, n, lFemenino=0):
    
        # Localizar los billones    
        prim,resto = divmod(n,10L**12)
        if prim!=0:
            if prim==1:     cRes = "un billon"
            else:           cRes = self._amount_to_text(prim,0)+" billones" # Billones es masculino
    
            if resto!=0:    cRes += " "+self._amount_to_text(resto,lFemenino)
    
        else:
        # Localizar millones
            prim,resto = divmod(n,10**6)
            if prim!=0:
                if prim==1: cRes = "un millon"
                else:       cRes = self._amount_to_text(prim,0)+" millones" # Millones es masculino
    
                if resto!=0: cRes += " " + self._amount_to_text(resto,lFemenino)
    
            else:
            # Localizar los miles
                prim,resto = divmod(n,10**3)
                if prim!=0:
                    if prim==1: cRes="mil"
                    else:       cRes=self._amount_to_text(prim,lFemenino)+" mil"
    
                    if resto!=0: cRes += " " + self._amount_to_text(resto,lFemenino)
    
                else:
                # Localizar los cientos
                    prim,resto=divmod(n,100)
                    if prim!=0:
                        if prim==1:
                            if resto==0:        cRes="cien"
                            else:               cRes="ciento"
                        else:
                            cRes=self._n3[prim-1]
                            if lFemenino:       cRes+="ientas"
                            else:               cRes+="ientos"
    
                        if resto!=0:  cRes+=" "+self._amount_to_text(resto,lFemenino)
    
                    else:
                    # Localizar las decenas
                        if lFemenino and n==1:              cRes="una"
                        elif n<=20:                         cRes=self._n1[n-1]
                        else:
                            prim,resto=divmod(n,10)
                            cRes=self._n2[prim-1]
                            if resto!=0:
                                if prim==2:                 cRes+=self._n11[resto-1]
                                else:                       cRes+=" y "+self._n1[resto-1]
    
                                if lFemenino and resto==1:  cRes+="a"
        return cRes

    def get_amount_to_text(self, amount, lang, currency=""):
	if currency.upper() in ('MXP', 'MXN', 'PESOS', 'PESOS MEXICANOS'):
		sufijo = 'M. N.'
        	currency = 'PESOS'
	else:
        	sufijo = ''
    	# return amount_to_text(amount, lang, currency)
    	amount_text = amount_to_text().amount_to_text_cheque(
        amount, currency, sufijo)
        amount_text = amount_text and amount_text.title() or ''
	return amount_text


class report_print_check(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_print_check, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'pages': self.get_pages,
        })

    def fill_line(self,payment, amount_str):
        if payment.journal_id.type=='bank' and  payment.currency_id and  payment.currency_id.name=='DOP':
            amount_str = amount_to_text().get_amount_to_text(payment.amount,lang='es_AR')
        return amount_str and (amount_str+' ').ljust(200, LINE_FILLER) or ''

    def get_pages(self, payment):
        """ Returns the data structure used by the template : a list of dicts containing what to print on pages.
        """
        stub_pages = self.make_stub_pages(payment)
        multi_stub = payment.company_id.us_check_multi_stub
        pages = []
        for i in range(0, stub_pages != None and len(stub_pages) or 1):
            pages.append({
                'sequence_number': payment.check_number\
                    if (payment.journal_id.check_manual_sequencing and payment.check_number != 0)\
                    else False,
                'payment_date': payment.payment_date,
                'partner_name': payment.partner_id.name,
                'currency': payment.currency_id,
                'amount': payment.amount if i == 0 else 'VOID',
                'amount_in_word': self.fill_line(payment,payment.check_amount_in_words) if i == 0 else 'VOID',
                'memo': payment.communication,
                'stub_cropped': not multi_stub and len(payment.invoice_ids) > INV_LINES_PER_STUB,
                # If the payment does not reference an invoice, there is no stub line to display
                'stub_lines': stub_pages != None and stub_pages[i],
            })
        return pages

    def make_stub_pages(self, payment):
        """ The stub is the summary of paid invoices. It may spill on several pages, in which case only the check on
            first page is valid. This function returns a list of stub lines per page.
        """
        if len(payment.invoice_ids) == 0:
            return None

        multi_stub = payment.company_id.us_check_multi_stub

        invoices = payment.invoice_ids.sorted(key=lambda r: r.date_due)
        debits = invoices.filtered(lambda r: r.type == 'in_invoice')
        credits = invoices.filtered(lambda r: r.type == 'in_refund')

        # Prepare the stub lines
        if not credits:
            stub_lines = [self.make_stub_line(payment, inv) for inv in invoices]
        else:
            stub_lines = [{'header': True, 'name': "Bills"}]
            stub_lines += [self.make_stub_line(payment, inv) for inv in debits]
            stub_lines += [{'header': True, 'name': "Refunds"}]
            stub_lines += [self.make_stub_line(payment, inv) for inv in credits]

        # Crop the stub lines or split them on multiple pages
        if not multi_stub:
            # If we need to crop the stub, leave place for an ellipsis line
            num_stub_lines = len(stub_lines) > INV_LINES_PER_STUB and INV_LINES_PER_STUB-1 or INV_LINES_PER_STUB
            stub_pages = [stub_lines[:num_stub_lines]]
        else:
            stub_pages = []
            i = 0
            while i < len(stub_lines):
                # Make sure we don't start the credit section at the end of a page
                if len(stub_lines) >= i+INV_LINES_PER_STUB and stub_lines[i+INV_LINES_PER_STUB-1].get('header'):
                    num_stub_lines = INV_LINES_PER_STUB-1 or INV_LINES_PER_STUB
                else:
                    num_stub_lines = INV_LINES_PER_STUB
                stub_pages.append(stub_lines[i:i+num_stub_lines])
                i += num_stub_lines

        return stub_pages

    def make_stub_line(self, payment, invoice):
        """ Return the dict used to display an invoice/refund in the stub
        """
        # Find the account.partial.reconcile which are common to the invoice and the payment
        if invoice.type in ['in_invoice', 'out_refund']:
            invoice_sign = 1
            invoice_payment_reconcile = invoice.move_id.line_ids.mapped('matched_debit_ids').filtered(lambda r: r.debit_move_id in payment.move_line_ids)
        else:
            invoice_sign = -1
            invoice_payment_reconcile = invoice.move_id.line_ids.mapped('matched_credit_ids').filtered(lambda r: r.credit_move_id in payment.move_line_ids)

        if payment.currency_id != payment.journal_id.company_id.currency_id:
            amount_paid = abs(sum(invoice_payment_reconcile.mapped('amount_currency')))
        else:
            amount_paid = abs(sum(invoice_payment_reconcile.mapped('amount')))

        return {
            'due_date': invoice.date_due,
            'number': invoice.reference and invoice.number + ' - ' + invoice.reference or invoice.number,
            'amount_total': invoice_sign * invoice.amount_total,
            'amount_residual': invoice_sign * invoice.residual,
            'amount_paid': invoice_sign * amount_paid,
            'currency': invoice.currency_id,
        }


class print_check_top(osv.AbstractModel):
    _name = 'report.l10n_us_check_printing.print_check_top'
    _inherit = 'report.abstract_report'
    _template = 'l10n_us_check_printing.print_check_top'
    _wrapped_report_class = report_print_check

class print_check_middle(osv.AbstractModel):
    _name = 'report.l10n_us_check_printing.print_check_middle'
    _inherit = 'report.abstract_report'
    _template = 'l10n_us_check_printing.print_check_middle'
    _wrapped_report_class = report_print_check

class print_check_bottom(osv.AbstractModel):
    _name = 'report.l10n_us_check_printing.print_check_bottom'
    _inherit = 'report.abstract_report'
    _template = 'l10n_us_check_printing.print_check_bottom'
    _wrapped_report_class = report_print_check
