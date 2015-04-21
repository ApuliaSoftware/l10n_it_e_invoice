# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Andre@ (<a.gallina@cgsoftware.it>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


import logging
import os
from ftplib import FTP
import datetime

from openerp import models, fields, api, _
from openerp.exceptions import Warning


_logger = logging.getLogger('Sending E-Invoice')


class WizardSendInvoice(models.TransientModel):

    _name = "wizard.send.invoice"
    _description = "Wizard For Sending E-Invoice"

    def create_report(self, cr, uid, res_ids,
                      report_name=False, file_name=False,
                      data=False, context=False):
        if not report_name or not res_ids:
            return (
                False,
                Exception('Report name and Resources ids are required !!!'))
        try:
            ret_file_name = '/tmp/%s.pdf' % file_name
            service = netsvc.LocalService("report.%s" % report_name)
            (result, format) = service.create(cr, uid, res_ids, data, context)
            fp = open(ret_file_name, 'wb+')
            fp.write(result)
            fp.close()
        except Exception, e:
            print 'Exception in create report:', e
            return (False, str(e))
        return (True, ret_file_name)

    def upload_file(self, cr, uid, ftp_vals, folder, file_name, context):
        try:
            ftp = FTP()
            ftp.connect(ftp_vals[0], int(ftp_vals[1]))
            ftp.login(ftp_vals[2], ftp_vals[3])
            try:
                ftp.cwd('%s%s' % (ftp_vals[4], folder))
                # move to the desired upload directory
                _logger.info('Currently in: %s', ftp.pwd())
                _logger.info('Uploading: %s', file_name)
                fullname = file_name
                name = os.path.split(fullname)[1]
                f = open(fullname, "rb")
                ftp.storbinary('STOR ' + name, f)
                f.close()
                _logger.info('Done!')
            finally:
                _logger.info('Close FTP Connection')
                ftp.quit()
        except:
            raise osv.except_osv('Error', 'Error to FTP')

    @api.multi
    def send_invoice(self):
        company_model = self.env['res.company']
        ftp_vals = company_model.get_ftp_vals()
        print '===================', ftp_vals
        company = self.env.user.company_id
        print '===================', company
        folder = 'imput flusso PDF'
        # company_obj = self.pool['res.company']
        # ftp_vals = company_obj.get_ftp_vals(cr, uid, False, context)
        # company = self.pool['res.users'].browse(cr, uid, uid).company_id
        # # ---- Setting the folder where put pdf file
        # folder = 'input flusso PDF'
        #
        # # ---- Select the printing module to print and create PDF
        # invoice_ids = context.get('active_ids', [])
        # invoice_obj = self.pool.get('account.invoice')
        # invoice = invoice_obj.browse(cr, uid, invoice_ids, context)[0]
        # report_name = invoice.journal_id.printing_module.report_name or False
        #
        # # ---- check if invoice can be send to SDI
        # if not invoice.journal_id.e_invoice:
        #     raise osv.except_osv(
        #         _('Error'),
        #         _('Is not E-Invoice check your Journal config!'))
        # if invoice.einvoice_state not in ('draft', 'sent'):
        #     raise osv.except_osv(
        #         _('Error!'),
        #         _('invoice has already been processed, \
        #            you can not proceed to send!'))
        # file_name = invoice.company_id.partner_id.vat
        # file_name += invoice.number.replace('/', '_')
        # if company.sending_type == 'pdf':
        #     # ---- Standard for file name is:
        #     # ---- ITpartita_iva_mittente<...>.pdf
        #     report = self.create_report(
        #         cr, uid, invoice_ids, report_name, file_name, False, context)
        #     report_file = report[0] and [report[1]] or []
        #     if not report_file:
        #         raise osv.except_osv(
        #             _('Error'),
        #             _('PDF is not ready!'))
        #     self.upload_file(
        #         cr, uid, ftp_vals, folder, report_file[0], context)
        # else:
        #     # Now sending XML file
        #     xml_create = self.pool['wizard.export.fatturapa'].exportFatturaPA(
        #         cr, uid, ids, context={'active_ids': [invoice.id]})
        #     attach_id = xml_create.get('res_id', False)
        #     try:
        #         data = self.pool['fatturapa.attachment.out'].browse(
        #             cr, uid, attach_id).ir_attachment_id.datas.decode('base64')
        #         file = '/tmp/' + file_name + '.xml'
        #         fp = open(file, 'wb+')
        #         fp.write(data)
        #         fp.close()
        #     except Exception, e:
        #         raise osv.except_osv(
        #             _('Error'),
        #             _('%s' %e))
        #     self.upload_file(cr, uid, ftp_vals, folder, file, context)
        #
        # history = invoice.history_ftpa or ''
        # history = '%s\n' % (history)
        # history = "%sFattura inviata in data %s" % (
        #     history, str(datetime.datetime.today()))
        # invoice_obj.write(
        #     cr, uid, invoice_ids[0],
        #     {'history_ftpa': history, 'einvoice_state': 'sent'}, context)
        #
        return {'type': 'ir.actions.act_window_close'}
