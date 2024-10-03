from odoo import fields, models

class OllamaModel(models.Model):
    _name = 'ollama.model'
    _description = 'Ollama Model'

    name = fields.Char(string='Model Name')
    server_url = fields.Char(string='Server URL')
    prompt_template = fields.Char(string='Prompt Template')

class OllamaTemp(models.Model):
    _name = 'ollama.tempreture'
    _description = "Ollama Tempreture"

    name = fields.Float(string="Tempreture", required=True)