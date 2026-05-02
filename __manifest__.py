{
    'name': 'Technical Order',
    'version': '17.0.1.0.0',
    'category': 'Sales',
    'summary': 'Manage Technical Orders for Wooden Tools Store',
    'author': 'Alaa Khaled',
    'depends': [
        'base',
        'sale_management',
        'mail',
    ],
    'data': [
         'security/ir.model.access.csv',
         'views/technical_order_views.xml',
         'wizard/reject_wizard_views.xml',
         'report/technical_order_report.xml',
         'views/menu.xml',
         'data/sequence.xml'
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}