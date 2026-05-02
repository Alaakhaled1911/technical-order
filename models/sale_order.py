from odoo import models, fields, api
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    technical_order_id = fields.Many2one(
        'technical.order',
        string='Technical Order'
    )

    @api.constrains('order_line', 'state')
    def _check_quantities(self):
        for so in self:
            if not so.technical_order_id:
                continue
            to = so.technical_order_id
            for line in so.order_line:
                to_line = to.order_line_ids.filtered(
                    lambda l: l.product_id == line.product_id
                )
                if not to_line:
                    continue
                confirmed_qty = sum(
                    sl.product_uom_qty
                    for s in to.so_ids.filtered(
                        lambda s: s.state == 'sale' and s.id != so.id
                    )
                    for sl in s.order_line
                    if sl.product_id == line.product_id
                )
                max_qty = to_line[0].quantity - confirmed_qty
                if line.product_uom_qty > max_qty:
                    raise ValidationError(
                        f'Quantity for {line.product_id.name} cannot exceed {max_qty} '
                        f'(remaining from Technical Order)'
                    )