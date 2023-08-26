import os, sys, json
from typing import Optional
from embedchain import CustomApp
from embedchain.config import(AddConfig,ChatConfig, ChunkerConfig)
from loguru import logger
from embedchain.models import Providers, EmbeddingFunctions
from string import Template
from dotenv import load_dotenv

from MyAppConfig import MyAzureOpenAIAppConfig
load_dotenv("deployment.env")

@logger.catch
def get_azure_openai_app_config():
  return MyAzureOpenAIAppConfig(
      embedding_fn=EmbeddingFunctions.OPENAI,
      provider=Providers.AZURE_OPENAI,
      log_level="DEBUG",
      deployment_name=os.getenv("EMBEDDING_DEPLOYMENT_NAME")
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
    chunker_config = AddConfig(chunker=ChunkerConfig(chunk_size=300, chunk_overlap=30)) #for TEXT
    bot.add("https://en.wikipedia.org/wiki/A._W._Peet", config=chunker_config)
    bot.add("https://www.trinity.utoronto.ca/directory/peet-a-w/", config=chunker_config)
    bot.add("https://www.youtube.com/watch?v=gBYcM9fe8YA","youtube_video")


@logger.catch
def query(q):
   return str(q)

@logger.catch
def bot_response(bot, query, chat_config):
  return bot.chat(query, config=chat_config)


@logger.catch
def main():
    TEMPERATURE = 0
    MAX_TOKENS = 1500
    NUMBER_DOCUMENTS = 3 #how many documents to retrieve from the database

    bot = CustomApp(get_azure_openai_app_config())
    void_load_documents(bot)
    chat_config = ChatConfig(
        template=get_custom_prompt_template(),
        number_documents=NUMBER_DOCUMENTS,# default is set to 1 by parent class QueryConfig
        model="gpt-3.5-turbo",
        temperature=TEMPERATURE, # default is set to 0 by parent class QueryConfig
        max_tokens=MAX_TOKENS, # default is set to 1000 by parent class QueryConfig
        top_p=None,
        stream=False,
        deployment_name=os.getenv("DEPLOYMENT_NAME")
    )
    q = query("What does Professor Peet research?")
    response = bot_response(bot, q, chat_config=chat_config)
    print(q,"\n",response)

if __name__ == '__main__':
    logger.add(sys.stderr, colorize=True, format="<green>{time}</green> <level>{message}</level>", level="DEBUG")
    main()


