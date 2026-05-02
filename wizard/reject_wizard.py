from odoo import models, fields


class RejectWizard(models.TransientModel):
    _name = 'reject.wizard'
    _description = 'Rejection Reason Wizard'

    order_id = fields.Many2one(
        'technical.order',
        string='Technical Order'
    )

    rejection_reason = fields.Text(
        string='Rejection Reason',
        required=True
    )

    def action_confirm(self):
        self.order_id.state = 'reject'
        self.order_id.rejection_reason = self.rejection_reason
        return {'type': 'ir.actions.act_window_close'}

    def action_cancel (self):
        return {'type': 'ir.actions.act_window_close'}





