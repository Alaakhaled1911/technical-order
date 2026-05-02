from odoo import models, fields, api

class TechnicalOrder(models.Model):
    _name = 'technical.order'
    _description = 'Technical Order'

    ref = fields.Char(
        string='Reference',
        required=True,
        default='New'
    )
    order_line_ids = fields.One2many(
        'technical.order.line',
        'order_id',
        string='Order Lines'
    )
    so_ids = fields.One2many(
        'sale.order',
        'technical_order_id',
        string='Sale Orders'
    )
    all_quantities_taken = fields.Boolean(
        string='All Quantities Taken',
        compute='_compute_all_quantities_taken'
    )
    so_count = fields.Integer(
        string='SO Count',
        compute='_compute_so_count'
    )

    request_name=fields.Char(
        string='Request Name',
        required=True
    )
    requested_by = fields.Many2one(
        'res.users',
        string='Requested By',
        required=True,
        default=lambda self: self.env.user
    )
    customer=fields.Many2one(
        'res.partner',
        string='Customer',
        required=True,

    )
    start_date=fields.Date(
        string='Start Date',
        required=True,
        default=fields.Date.today()
    )
    end_date=fields.Date(
        string='End Date'
    )
    rejection_reason=fields.Text(
        string='Rejection Reason',
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('to_be_approved', 'To Be Approved'),
        ('approve', 'Approved'),
        ('reject', 'Rejected'),
        ('cancel', 'Cancelled'),
    ], string='Status',
        default='draft',
        tracking=True
    )

    total_price = fields.Float(
        compute='_compute_total_price',
        string='Total Price',
        store=True
    )

    def _compute_so_count(self):
        for rec in self:
            rec.so_count = len(rec.so_ids)

    def _compute_all_quantities_taken(self):
        for rec in self:
            all_taken = True
            for line in rec.order_line_ids:
                confirmed_qty = sum(
                    so_line.product_uom_qty
                    for so in rec.so_ids.filtered(lambda s: s.state == 'sale')
                    for so_line in so.order_line
                    if so_line.product_id == line.product_id
                )
                if confirmed_qty < line.quantity:
                    all_taken = False
                    break
            rec.all_quantities_taken = all_taken

    def _get_remaining_quantities(self):
        remaining = {}
        for line in self.order_line_ids:
            confirmed_qty = sum(
                so_line.product_uom_qty
                for so in self.so_ids.filtered(lambda s: s.state == 'sale')
                for so_line in so.order_line
                if so_line.product_id == line.product_id
            )
            remaining[line.product_id.id] = line.quantity - confirmed_qty
        return remaining

    def action_create_so(self):
        remaining = self._get_remaining_quantities()
        so_lines = []
        for line in self.order_line_ids:
            remaining_qty = remaining.get(line.product_id.id, 0)
            if remaining_qty > 0:
                so_lines.append((0, 0, {
                    'product_id': line.product_id.id,
                    'name': line.description,
                    'product_uom_qty': remaining_qty,
                    'price_unit': line.price,
                }))
        so = self.env['sale.order'].create({
            'partner_id': self.customer.id,
            'technical_order_id': self.id,
            'order_line': so_lines,
        })

    def action_view_so(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'tree,form',
            'domain': [('technical_order_id', '=', self.id)],
        }


    @api.depends('order_line_ids.total')
    def _compute_total_price(self):
        for order in self:
            order.total_price = sum(order.order_line_ids.mapped('total'))

    def action_cancel (self):
        self.state='cancel'


    def action_draft (self):
        self.state='draft'

    def action_reject (self):
        return {
            'type':'ir.actions.act_window',
            'name':'Rejection Reason',
            'res_model':'reject.wizard',
            'target':'new',
            'view_mode':'form',
            'context': {'default_order_id': self.id},

        }



    def action_submit (self):
        self.state='to_be_approved'

    def action_approve (self):
        self.state='approve'
        sale_manager_group = self.env.ref('sales_team.group_sale_manager')
        users = sale_manager_group.users
        email_list  = ','.join([user.email for user in users if user.email])
        mail = self.env['mail.mail'].create({
            'subject': f'Technical Order {self.request_name} has been approved',
            'body_html': f'<p>Technical Order <b>{self.request_name}</b> has been approved</p>',
            'email_to': email_list,
        })
        mail.send()





    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.ref == 'New':
                rec.ref = self.env['ir.sequence'].next_by_code('technical.order.number') or 'New'
        return records
        




