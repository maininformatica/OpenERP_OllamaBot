from odoo import fields, models, api
import requests
from odoo.exceptions import UserError


def get_ollama_models(server_url):
    try:
        response = requests.get(f"{server_url}/api/tags")
        response.raise_for_status()
        models_data = response.json()
        models = [model["name"] for model in models_data["models"]]
        return models
    except requests.exceptions.RequestException as e:
        raise UserError(f"Error al obtener los modelos del servidor: {e}")
    except KeyError as e:
        raise UserError(f"Error al procesar los datos de respuesta: {e}")


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    def _get_default_tempreture(self):
        return self.env.ref('ollama_bot.ollama_tempreture_6').id

    server_url = fields.Char(
        string="URL Servidor",
        help="http://YourServerIP:11434/",
        config_parameter="ollama_bot.server_url",
        required=True,
    )

    prompt_template = fields.Char(
        string="Prompt Template",
        help="""You are an AI language model assistant. Your task is to generate five
                different versions of the given user question.""",
        config_parameter="ollama_bot.prompt_template",
        required=True,
        default="""You are an AI language model assistant. Your task is to generate five
                different versions of the given user question. """
    )

    ollama_model_id = fields.Many2one(
        "ollama.model",
        string="Ollama Model",
        config_parameter="ollama_bot.ollama_model_id",
    )

    tempreture_id = fields.Many2one(
        "ollama.tempreture",
        string="Temperatura del Modelo",
        help="Configura la temperatura del modelo Ollama.",
        config_parameter="ollama_bot.tempreture_id",
        
    )


    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        server_url = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("ollama_bot.server_url", default="")
        )
        res.update(server_url=server_url)
        return res

    def update_ollama_models(self):
        if self.server_url:
            try:
                models = get_ollama_models(self.server_url)
                OllamaModel = self.env["ollama.model"]
                existing_models = OllamaModel.sudo().search([])

                # Borrar los modelos existentes si la URL del servidor ha cambiado
                if existing_models and existing_models[0].server_url != self.server_url:
                    existing_models.unlink()

                # Crear nuevos modelos
                for model in models:
                    OllamaModel.create(
                        {"name": model, "server_url": self.server_url}
                    )

                # Reset the selection if the current model is not in the updated list
                if self.ollama_model_id and self.ollama_model_id.name not in models:
                    self.ollama_model_id = None
            except UserError as e:
                # Manejar el error levantado por get_ollama_models
                OllamaModel = self.env["ollama.model"]
                OllamaModel.sudo().search([]).unlink()
                self.ollama_model_id = None
                raise UserError(f"Error al actualizar los modelos: {e}")

    def execute(self):
        res = super().execute()
        self.update_ollama_models()
        return res
