import requests
from odoo import models, _
from odoo.exceptions import UserError
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_models import ChatOllama
from langchain_core.runnables import RunnablePassthrough, RunnableSequence
from langchain_community.vectorstores import Chroma
from langchain.retrievers.multi_query import MultiQueryRetriever

class CommunicationChannel(models.Model):
    _inherit = 'mail.channel'

    def _notify_thread(self, message, msg_vals=False, **kwargs):
        rdata = super(CommunicationChannel, self)._notify_thread(message, msg_vals=msg_vals, **kwargs)
        ollama_channel_id = self.env.ref('ollama_bot.channel_ollama')
        user_ollama = self.env.ref("ollama_bot.user_ollama")
        partner_ollama = self.env.ref("ollama_bot.partner_ollama")
        author_id = msg_vals.get('author_id')
        ollama_name = str(partner_ollama.name or '') + ', '
        prompt = msg_vals.get('body')

        if not prompt:
            return rdata

        Partner = self.env['res.partner']
        partner_name = ''
        if author_id:
            partner_id = Partner.browse(author_id)
            if partner_id:
                partner_name = partner_id.name

        if self.channel_type == 'chat':
            if (author_id != partner_ollama.id and
                    (ollama_name in msg_vals.get('record_name', '') or 'Ollama,' in msg_vals.get('record_name', ''))):
                try:
                    res = self._get_ollama_response(prompt=prompt)
                    self.with_user(user_ollama).message_post(body=res, message_type='comment', subtype_xmlid='mail.mt_comment')
                except Exception as e:
                    raise UserError(_(e))

        elif msg_vals.get('model', '') == 'mail.channel' and msg_vals.get('res_id', 0) == ollama_channel_id.id:
            if author_id != partner_ollama.id:
                try:
                    res = self._get_ollama_response(prompt=prompt)
                    ollama_channel_id.with_user(user_ollama).message_post(body=res, message_type='comment', subtype_xmlid='mail.mt_comment')
                except Exception as e:
                    raise UserError(_(e))
        return rdata
    
    def _get_ollama_response(self, prompt):
        # Url del servidor ollama
        ICP = self.env['ir.config_parameter'].sudo()
        server_url = ICP.get_param('ollama_bot.server_url')
        ollama_model_id = ICP.get_param('ollama_bot.ollama_model_id')
        tempreture_id = ICP.get_param('ollama_bot.tempreture_id')
        tempreture = self.env['ollama.tempreture'].browse(int(tempreture_id)).name
        prompt_template = ICP.get_param('ollama_bot.prompt_template')
        
        try:
            if ollama_model_id:
                ollama_model = self.env['ollama.model'].browse(int(ollama_model_id)).name
        except Exception as ex:
            ollama_model = 'llama3'
            pass

        try:
            llm = ChatOllama(model=ollama_model, base_url=server_url, temperature=tempreture)
        except requests.exceptions.RequestException as e:
            return "Por favor escriba una URL válida."
        except Exception as e:  # Catch other potential exceptions
            return e 

        # Procesar la pregunta sin archivos adjuntos
        template = prompt_template + "\nQuestion: {question}"
        prompt_template = ChatPromptTemplate.from_template(template)

        chain = RunnableSequence(
            {"question": RunnablePassthrough()},
            prompt_template,
            llm,
            StrOutputParser()
        )

        # Obtener la respuesta usando la función definida anteriormente
        response = chain.invoke({"question": prompt})

        return response
