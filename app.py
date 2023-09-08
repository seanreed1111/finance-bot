
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
def get_azure_openai_app_config():
  return MyAzureOpenAIAppConfig(
      embedding_fn=EmbeddingFunctions.OPENAI,
      log_level="DEBUG",
      deployment_name=os.getenv("EMBEDDING_DEPLOYMENT_NAME"),
      provider=Providers.AZURE_OPENAI
  )

def get_custom_prompt_template():
    from string import Template

    DEFAULT_PROMPT = """
    You are a chatbot having a conversation. You are given chat
    history and context.
    You need to answer the query considering context,
    chat history and your knowledge base.
    If you don't know the answer or the answer is neither contained in the context
    nor in history, then simply say "No idea, bro".

    $context

    History: $history

    Query: $query

    Helpful Answer:
    """

    return Template(DEFAULT_PROMPT)

@logger.catch
def void_load_documents(bot):
    chunker_config = AddConfig(chunker=ChunkerConfig(chunk_size=1100, chunk_overlap=150))
    bot.add("./DATA/dora.pdf", config=chunker_config, data_type="pdf_file")
#    bot.add("https://en.wikipedia.org/wiki/A._W._Peet", config=chunker_config)
#    bot.add("https://www.trinity.utoronto.ca/directory/peet-a-w/", config=chunker_config)
    #bot.add("https://www.youtube.com/watch?v=gBYcM9fe8YA","youtube_video")
#    bot.add("https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=CELEX:32022R2554", config=chunker_config)

@logger.catch
def query(q):
   return str(q)

@logger.catch
def main():
    TEMPERATURE = 0
#    MAX_TOKENS = 3000
    NUMBER_DOCUMENTS = 3 #how many documents to retrieve from the database

    bot = CustomApp(get_azure_openai_app_config())
    void_load_documents(bot)
    chat_config = ChatConfig(
        number_documents=NUMBER_DOCUMENTS,# default is set to 1 by parent class QueryConfig
        model="gpt-3.5-turbo",
        temperature=TEMPERATURE, # default is set to 0 by parent class QueryConfig
        top_p=None,
        stream=False,
        deployment_name=os.getenv("DEPLOYMENT_NAME")
    )

    @logger.catch
    def bot_response(message, history):
        answer = bot.chat(message,config=chat_config)
       # print(message, "\n", bot.memory.chat_memory)
       # print(type(message), "\n", type(bot.memory.chat_memory))
        history.append((message, answer))
        return "", history

#    print("chat_memory=\n", bot.memory.chat_memory)

    with gr.Blocks() as demo:
        chatbot = gr.Chatbot(height=200)
        msg = gr.Textbox(label="Query")
        btn = gr.Button("Submit")
        clear = gr.ClearButton(components=[msg, chatbot], value="Clear console")
        btn.click(bot_response, inputs=[msg, chatbot], outputs=[msg, chatbot])
        msg.submit(bot_response, inputs=[msg, chatbot], outputs=[msg, chatbot])
    gr.close_all()
#    demo = gr.ChatInterface(bot_response, title="DORABot")

    launch = demo.launch(server_port=8501, share=True, show_error=True)
    logger.info(f"{launch}")
    print("launch", launch)

if __name__ == '__main__':
    log_level = "INFO"
    logger.add(sys.stderr, colorize=True, format="<green>{time}</green> <level>{message}</level>", level=log_level)
    main()
