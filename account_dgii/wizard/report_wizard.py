# -*- coding: utf-8 -*-
import xlsxwriter
import base64
import sys
from openerp import api, fields, models, _
import datetime
from calendar import monthrange

class InvoiceReportService(models.TransientModel): 
    _name = 'account.invoice.report.service'

    @api.multi
    def _calculate_year(self):
        year = datetime.date.today().strftime("%Y")
        return [(str(int(year)-5), str(int(year)-5)),
                (str(int(year)-4), str(int(year)-4)),
                (str(int(year)-3), str(int(year)-3)),
                (str(int(year)-2), str(int(year)-2)),
                (str(int(year)-1), str(int(year)-1)),
                (str(int(year)), str(int(year))),
                (str(int(year) +1), str(int(year)+1)),
                (str(int(year)+2), str(int(year)+2)),
                (str(int(year)+3), str(int(year)+3)),
                (str(int(year)+4), str(int(year)+4)),
                (str(int(year)+5), str(int(year)+5)),]

    invoice_data = fields.Char('Name')
    file_name = fields.Binary('Invoice Report', readonly=True)
    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date")
    month = fields.Selection([('01','01'),
                                ('02','02'),
                                ('03','03'),
                                ('04','04'),
                                ('05','05'),
                                ('06','06'),
                                ('07','07'),
                                ('08','08'),
                                ('09','09'),
                                ('10','10'),
                                ('11','11'),
                                ('12','12')],string="Month")
    year = fields.Selection(_calculate_year,string="Year",default=datetime.date.today().strftime("%Y"))

    @api.multi
    def generate_report(self):
        invoice_ids = self.env[('account.invoice')].search([])
        if self.month:
            start_date = '01/'+ str(self.month) +"/" + str(self.year)
            start_date = datetime.datetime.strptime(start_date, "%d/%m/%Y")
            month_day = monthrange(int(self.year),int(self.month))
            end_date = start_date + datetime.timedelta(days=int(month_day[1]))
            invoice_ids = self.env[('account.invoice')].search([('date_invoice','>=',start_date),('date_invoice','<=',end_date)])
        return {
            'name': _('Invoice Report'),
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'account.invoice',
            'view_id': self.env.ref('account_dgii.account_invoice_tree_report').id,
            'type': 'ir.actions.act_window',
            'domain':[('type','in',['in_invoice','in_refund']),('state','not in',['draft','cancel']),('id','in',invoice_ids and invoice_ids.ids or [])],
            'target': 'current',
            'context':{'category':True,'period':str(self.year)+str(self.month)}
        }

    @api.multi
    def print_report(self):
        context = dict(self._context or {})
        tmp_name = ''
        f_name = ''
        tmp_name='/tmp/invoice_report.xlsx'
        f_name = 'invoice_report.xlsx'

        workbook = xlsxwriter.Workbook(tmp_name)
        worksheet = workbook.add_worksheet()
        row = 0
        col = 0
        url_format = workbook.add_format({'bold':1})
        total_time_xl = []
        #1
        worksheet.write(row, col, 'Lineas', url_format)
        worksheet.set_column(row, col, 20)
        col += 1
        #2
        worksheet.write(row, col, 'Tax ID for Suppliers', url_format)
        worksheet.set_column(row, col, 20)
        col += 1
        #3
        worksheet.write(row, col, 'Tipo Id', url_format)
        worksheet.set_column(row, col, 20)
        col += 1
        #4
        worksheet.write(row, col, 'Tipo Bienes y Servicios Comprados', url_format)
        worksheet.set_column(row, col, 20)
        col += 1
        #5
        worksheet.write(row, col, 'NCF', url_format)
        worksheet.set_column(row, col, 20)
        col += 1
        #6
        worksheet.write(row, col, 'NCF Documento Modificado', url_format)
        worksheet.set_column(row, col, 20)
        col += 1
        #7
        worksheet.merge_range('G1:H1', 'Fecha Comprobante', url_format)
        worksheet.set_column(row, col, 20)
        col += 2
        #8
        worksheet.merge_range('I1:J1', 'Fecha Pago', url_format)
        worksheet.set_column(row, col, 20)
        col += 2
        #9
        worksheet.write(row, col, 'Itbis Facturado', url_format)
        worksheet.set_column(row, col, 20)
        col += 1
        #10
        worksheet.write(row, col, 'Itbis Retenido', url_format)
        worksheet.set_column(row, col, 20)
        col += 1
        #11
        worksheet.write(row, col, 'Monto Facturado', url_format)
        worksheet.set_column(row, col, 20)
        col += 1
        #12
        worksheet.write(row, col, 'Retencion Renta', url_format)
        worksheet.set_column(row, col, 20)
        col += 1

        row += 1
        lines = 1
        for rowdata in self.env['account.invoice'].browse(self._context.get('active_ids')):
            col = 0
            worksheet.set_column(row, col, 10)
            worksheet.write(row, col,lines)
            col += 1
            tax = rowdata.supplier_tax_no if rowdata.supplier_tax_no != 0 else ''
            worksheet.write(row, col,tax)
            col += 1

            worksheet.write(row, col,rowdata.tipo_id)
            col += 1

            worksheet.write(row, col,rowdata.type_good_services_id.code)
            col += 1

            worksheet.write(row, col,rowdata.ncf_no)
            col += 1

            worksheet.write(row, col,rowdata.ncf_doc_modification)
            col += 1

            worksheet.write(row, col,rowdata.receipt_year)
            col += 1

            worksheet.write(row, col,rowdata.receipt_date)
            col += 1

            worksheet.write(row, col,rowdata.pay_year)
            col += 1

            worksheet.write(row, col,rowdata.pay_date)
            col += 1

            billed_tax = "%.2f" % rowdata.billed_tax
            worksheet.write(row, col,billed_tax)
            col += 1

            withheld_tax = "%.2f" % rowdata.withheld_tax
            worksheet.write(row, col,withheld_tax)
            col += 1

            amount_untaxed = "%.2f" % rowdata.amount_untaxed
            worksheet.write(row, col,amount_untaxed)
            col += 1

            retention_tax = "%.2f" % rowdata.retention_tax
            worksheet.write(row, col,retention_tax)
            col += 1
            row += 1
            lines +=1

        workbook.close()

        with open(tmp_name, 'r') as myfile:
            data = myfile.read()
            myfile.close()
        result = base64.b64encode(data)

        attachment_obj = self.env['ir.attachment']
        attachment_id = attachment_obj.create({'name': f_name, 'datas_fname': f_name, 'datas': result})
        download_url = '/web/content/'+str(attachment_id.id)+'?download=true'#'model=ir.attachment&field=datas&filename_field=name&id=' + str(attachment_id.id)
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')

        return {
            "type": "ir.actions.act_url",
            "url": str(base_url) + str(download_url),
            "target": "self",
        }

    @api.multi
    def print_text_report(self):
        try:
            file_name = '606'
            invoice_ids = self.env['account.invoice'].browse(self._context.get('active_ids'))
            
            year = datetime.datetime.strptime(invoice_ids[0].date_invoice, '%Y-%m-%d').strftime('%Y')
            month = datetime.datetime.strptime(invoice_ids[0].date_invoice, '%Y-%m-%d').strftime('%m')

            file_name = file_name + str(year) + str(month)

            name = file_name + '.txt'  # Name of text file coerced with +.txt
            file = open(name,'w+')   # Trying to create a new file or open one

            user_id = self.env.user
            company_id = user_id.company_id

            # ### Header Part ###
            # header_1 = 'Codigo Informacion'
            # header_2 = 'RNC o Cedula'
            # header_3 = 'Periodo'
            # header_4 = 'Cantidad Registros'

            # header_string = header_1 + " | " + header_2 + " | " + header_3 + " | " + header_4 + "\n"
            # file.write(header_string)

            # Company Detail
            rnc_no = ''
            if self.env.user and self.env.user.company_id:
                company = self.env.user.company_id
                if company.vat and len(company.vat) == 11:
                    rnc_no = company.vat

            header_val_1 = "606"
            header_val_2 = str(rnc_no)
            header_val_3 = str(year) + str(month or '')
            header_val_4 = str(len(invoice_ids))

            header_val_string = header_val_1 + "|" + header_val_2 + "|" + header_val_3 + "|" + header_val_4 + "\n"

            file.write(header_val_string)

            # inv_header_1 = 'RNC o Cedula'
            # inv_header_2 = 'Tipo Id'
            # inv_header_3 = 'Tipo Bienes y Servicios Comprados'
            # inv_header_4 = 'NCF'
            # inv_header_5 = 'NCF Documento Modificado'
            # inv_header_6 = 'Fecha Comprobante'
            # inv_header_7 = 'Fecha Pago'
            # inv_header_8 = 'Monto Facturado en Servicios'
            # inv_header_9 = 'Monto Facturado en Bienes'
            # inv_header_10 = 'Total Monto Facturado'
            # inv_header_11 = 'ITBIS Facturado'
            # inv_header_12 = 'Itbis Retenido'
            # inv_header_13 = 'ITBIS sujeto a Proporcionalidad (Art. 349)'
            # inv_header_14 = 'ITBIS llevado al Costo'
            # inv_header_15 = 'ITBIS por Adelantar'
            # inv_header_16 = 'ITBIS percibido en compras'
            # inv_header_17 = 'Tipo de Retención en ISR'
            # inv_header_18 = 'Monto Retención Renta'
            # inv_header_19 = 'ISR Percibido en compras'
            # inv_header_20 = 'Impuesto Selectivo al Consumo'
            # inv_header_21 = 'Otros Impuestos/Tasas'
            # inv_header_22 = 'Monto Propina Legal'
            # inv_header_23 = 'Forma de Pago'

            # inv_header_string = inv_header_1 + "|" + inv_header_2 + "|" + inv_header_3 + "|" + inv_header_4 + "|" \
            # + inv_header_5 + "|" + inv_header_6 + "|" + inv_header_7 + "|" + inv_header_8 + "|" + inv_header_9 + "|" \
            # + inv_header_10 + "|" + inv_header_11 + "|" + inv_header_12 + "|" + inv_header_13 + "|" \
            # + inv_header_14 + "|" + inv_header_15 + "|" + inv_header_16 + "|" + inv_header_17 + "|" \
            # + inv_header_18 + "|" + inv_header_19 + "|" + inv_header_20 + "|" + inv_header_21 + "|" \
            # + inv_header_22 + "|" + inv_header_23 + "\n"

            # file.write(inv_header_string)

            length = len(invoice_ids)
            for rowdata in invoice_ids:
                rnc = ''
                if rowdata.partner_id and rowdata.partner_id.is_company:
                    rnc = rowdata.partner_id.vat or ''
                else:
                    rnc = rowdata.partner_id.vat or ''

                inv_val_1 = rnc
                inv_val_2 = rowdata.tipo_id or ''
                inv_val_3 = rowdata.tipo or ''
                inv_val_4 = rowdata.ncf_no or ''
                inv_val_5 = rowdata.ncf_doc_modification or ''
                inv_val_6 = datetime.datetime.strptime(rowdata.date_invoice, '%Y-%m-%d').strftime('%Y%m%d')

                #7
                pay_date = ""
                if rowdata.pay_year and rowdata.pay_date:
                    pay_date = rowdata.pay_year + rowdata.pay_date
                
                inv_val_7 = "{:>6}".format(str(pay_date))
                
                #8 Total of service type product without tax
                total_monto_facturado_en_servicios = sum([line.quantity * line.price_unit for line in rowdata.invoice_line_ids if line.product_id and line.product_id.type == 'service'])
                inv_val_8 = total_monto_facturado_en_servicios
                
                # #9 Total of not service type product without tax
                total_monto_facturado_en_bienes = sum([line.quantity * line.price_unit for line in rowdata.invoice_line_ids if line.product_id and line.product_id.type != 'service'])
                inv_val_9 = total_monto_facturado_en_bienes

                #10 Total amount without tax
                inv_val_10 = rowdata.amount_untaxed

                # Tax Updates
                itbis_facturado_price = 0.00
                itbis_retenido_price = 0.00
                itbis_sujeto_troporcionalidad_price = 0.00
                itbis_llevado_price = 0.00
                monto_retencion_renta_price = 0.00
                impuesto_selectivo_al_consumo_price = 0.00
                otros_impuestos_price = 0.00
                monto_propina_legal_price = 0.00

                for line in rowdata.invoice_line_ids:
                    taxes = line.mapped("invoice_line_tax_ids")
                    itbis_facturado = taxes.filtered(lambda x: x.itbis_facturado)
                    itbis_retenido = taxes.filtered(lambda x: x.itbis_retenido)
                    itbis_sujeto_troporcionalidad = taxes.filtered(lambda x: x.itbis_sujeto_troporcionalidad)
                    itbis_llevado = taxes.filtered(lambda x: x.itbis_llevado)
                    monto_retencion_renta = taxes.filtered(lambda x: x.monto_retencion_renta)
                    impuesto_selectivo_al_consumo = taxes.filtered(lambda x: x.impuesto_selectivo_al_consumo)
                    otros_impuestos = taxes.filtered(lambda x: x.otros_impuestos)
                    monto_propina_legal = taxes.filtered(lambda x: x.monto_propina_legal)

                    price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                    
                    itbis_facturado_tax_data = itbis_facturado.compute_all(price, rowdata.currency_id or None , line.quantity, product=line.product_id, partner=rowdata.partner_id)
                    itbis_retenido_tax_data = itbis_retenido.compute_all(price, rowdata.currency_id or None , line.quantity, product=line.product_id, partner=rowdata.partner_id)
                    itbis_sujeto_troporcionalidad_tax_data = itbis_sujeto_troporcionalidad.compute_all(price, rowdata.currency_id or None , line.quantity, product=line.product_id, partner=rowdata.partner_id)
                    itbis_llevado_tax_data = itbis_llevado.compute_all(price, rowdata.currency_id or None , line.quantity, product=line.product_id, partner=rowdata.partner_id)
                    monto_retencion_renta_tax_data = monto_retencion_renta.compute_all(price, rowdata.currency_id or None , line.quantity, product=line.product_id, partner=rowdata.partner_id)
                    impuesto_selectivo_al_consumo_tax_data = impuesto_selectivo_al_consumo.compute_all(price, rowdata.currency_id or None , line.quantity, product=line.product_id, partner=rowdata.partner_id)
                    otros_impuestos_tax_data = otros_impuestos.compute_all(price, rowdata.currency_id or None , line.quantity, product=line.product_id, partner=rowdata.partner_id)
                    monto_propina_legal_tax_data = monto_propina_legal.compute_all(price, rowdata.currency_id or None , line.quantity, product=line.product_id, partner=rowdata.partner_id)
                    
                    itbis_facturado_price += sum([data['amount'] for data in itbis_facturado_tax_data['taxes']])
                    itbis_retenido_price += sum([data['amount'] for data in itbis_retenido_tax_data['taxes']])
                    itbis_sujeto_troporcionalidad_price += sum([data['amount'] for data in itbis_sujeto_troporcionalidad_tax_data['taxes']])
                    itbis_llevado_price += sum([data['amount'] for data in itbis_llevado_tax_data['taxes']])
                    monto_retencion_renta_price += sum([data['amount'] for data in monto_retencion_renta_tax_data['taxes']])
                    impuesto_selectivo_al_consumo_price += sum([data['amount'] for data in impuesto_selectivo_al_consumo_tax_data['taxes']])
                    otros_impuestos_price += sum([data['amount'] for data in otros_impuestos_tax_data['taxes']])
                    monto_propina_legal_price += sum([data['amount'] for data in monto_propina_legal_tax_data['taxes']])
                
                inv_val_11 = itbis_facturado_price
                inv_val_12 = itbis_retenido_price
                inv_val_13 = itbis_sujeto_troporcionalidad_price
                inv_val_14 = itbis_llevado_price
                inv_val_15 = itbis_facturado_price - itbis_llevado_price
                inv_val_16 = '0'
                inv_val_17 = ''
                inv_val_18 = monto_retencion_renta_price
                inv_val_19 = '0'
                inv_val_20 = impuesto_selectivo_al_consumo_price
                inv_val_21 = otros_impuestos_price
                inv_val_22 = monto_propina_legal_price
                inv_val_23 = ''

                inv_val_string = str(inv_val_1) + "|" + str(inv_val_2) + "|" + str(inv_val_3) + "|" + str(inv_val_4) + "|" + str(inv_val_5) \
                    + "|" + str(inv_val_6) + "|" + str(inv_val_7) + "|" + str(inv_val_8) + "|" + str(inv_val_9) + "|" + str(inv_val_10) \
                    + "|" + str(inv_val_11) + "|" + str(inv_val_12) + "|" + str(inv_val_13) + "|" + str(inv_val_14) + "|" + str(inv_val_15) \
                    + "|" + str(inv_val_16) + "|" + str(inv_val_17) + "|" + str(inv_val_18) + "|" + str(inv_val_19) + "|" + str(inv_val_20) + "|" \
                    + str(inv_val_21) + "|" + str(inv_val_22) + "|" + str(inv_val_23)

                if length > 1:
                    inv_val_string += "\n"
                    length -= 1
                file.write(inv_val_string)
            file.close()
        except:
            print('Something went wrong! Can\'t tell what?', sys.exc_info()[0])
            sys.exit(0) # quit Python
        with open(name, 'r') as myfile:
            data = myfile.read()
            myfile.close()
            result = base64.b64encode(data)

        # Files actions
        attach_vals = {'invoice_data': name, 'file_name': result}
        act_id = self.env['account.invoice.report.service'].create(attach_vals)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.invoice.report.service',
            'res_id': act_id.id,
            'view_type': 'form',
            'view_mode': 'form',
            'context': self.env.context,
            'target': 'new',
        }