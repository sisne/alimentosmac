from odoo import fields, models, api, _


class AccountPayment(models.Model):
    _inherit = "account.payment"
    
    state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted'), ('sent', 'Sent'), ('cancel', 'Cancelled'), ('reconciled', 'Reconciled')], readonly=True, default='draft', copy=False, string="Status")
    
    @api.multi
    def cancel(self):
        for rec in self:
            for move in rec.move_line_ids.mapped('move_id'):
                if rec.invoice_ids:
                    move.line_ids.remove_move_reconcile()
                move.button_cancel()
                move.unlink()
            rec.state = 'cancel'
    
    @api.multi
    def set_to_draft(self):
        for rec in self:
            rec.state = 'draft'
