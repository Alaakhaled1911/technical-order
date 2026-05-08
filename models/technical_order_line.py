from odoo import models, fields, api

class TechnicalOrderLine(models.Model):
    _name = 'technical.order.line'
    _description = 'Technical Order Line'

    product_id=fields.Many2one(
        'product.product',
        required=True,
        string='Product',
    )
    order_id=fields.Many2one('technical.order')
    description = fields.Char(
        string='Description',

    )
    quantity = fields.Float(
        default=1,
    )
    price = fields.Float(
        related='product_id.lst_price',
        store=True,
        readonly=True
    )
    total = fields.Float(
        readonly=True,
        string='Total',
        compute='_compute_total',
        store=True
    )



    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.description = self.product_id.name


            

    @api.depends('quantity', 'price')
    def _compute_total(self):
        for order in self:
            order.total = order.price * order.quantity



