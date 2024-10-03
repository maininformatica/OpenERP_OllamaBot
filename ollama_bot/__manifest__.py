# -*- coding: utf-8 -*-
{
    'name': "Ollama Bot",
    'summary': "Chat IA con Ollama",
    'description': """
        Este módulo expande las posibilidades de odooBot usando Ollama como principal motor de IA.
        Su principal función es añadir un chat bot dentro de odoo que permita hacer consultas rápidas.
    """,
    'author': "main informàtica (Rubén Bonilla)",
    'website': "https://www.main-informatica.com/",
    'category': 'Tools',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base','base_setup', 'mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/ollama_model_data.xml',
        'data/mail_channel_data.xml',
        'data/user_partner_data.xml',
        'views/res_config_settings_views.xml',
    ],   
    "application": True,
    "installable": True,
    "auto_install": False,
    "icon": "ollama_bot/static/description/icon.png",
}
