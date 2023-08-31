import os, sys, json
from typing import Optional
from embedchain.apps.CustomApp import CustomApp
from embedchain.config import(AddConfig,ChatConfig, ChunkerConfig)
from loguru import logger
from embedchain.models import Providers, EmbeddingFunctions
from string import Template
from dotenv import load_dotenv

from MyAppConfig import MyAzureOpenAIAppConfig
load_dotenv("deployment.env")
import gradio as gr

@logger.catch
def get_azure_openai_app_config(log_level="DEBUG"):
  return MyAzureOpenAIAppConfig(
      embedding_fn=EmbeddingFunctions.OPENAI,
      log_level=log_level,
      deployment_name=os.getenv("EMBEDDING_DEPLOYMENT_NAME"),
      provider=Providers.AZURE_OPENAI
  )

@logger.catch
def void_load_documents(bot):
    chunker_config = AddConfig(chunker=ChunkerConfig(chunk_size=1100, chunk_overlap=150))
    bot.add("https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=CELEX:32022R2554", config=chunker_config)

@logger.catch
def main(log_level="DEBUG"):
    TEMPERATURE = 0
    MAX_TOKENS = 3000
    NUMBER_DOCUMENTS = 3 #how many documents to retrieve from the database
    bot = CustomApp(get_azure_openai_app_config(log_level=log_level))
    void_load_documents(bot)
    chat_config = ChatConfig(
        number_documents=NUMBER_DOCUMENTS,# default is set to 1 by parent class QueryConfig
        model="gpt-3.5-turbo",
        temperature=TEMPERATURE, # default is set to 0 by parent class QueryConfig
        max_tokens=MAX_TOKENS, # default is set to 1000 by parent class QueryConfig
        top_p=None,
        stream=False,
        deployment_name=os.getenv("DEPLOYMENT_NAME")
    )

    @logger.catch
    def bot_response(message, history):
        answer = bot.chat(message,config=chat_config)
        history.append((message, answer))
        return "", history


    with gr.Blocks() as demo:
        chatbot = gr.Chatbot(height=200)
        msg = gr.Textbox(label="Query")
        btn = gr.Button("Submit")
        clear = gr.ClearButton(components=[msg, chatbot], value="Clear console")
        btn.click(bot_response, inputs=[msg, chatbot], outputs=[msg, chatbot])
        msg.submit(bot_response, inputs=[msg, chatbot], outputs=[msg, chatbot])
    gr.close_all()
#    demo = gr.ChatInterface(bot_response, title="DORABot")

    demo.launch(server_port=8501, share=True, debug=True)

if __name__ == '__main__':
    log_level = "WARNING"
    logger.add(sys.stderr, colorize=True, format="<green>{time}</green> <level>{message}</level>", level=log_level)
    main(log_level=log_level)