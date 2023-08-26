from typing import Any, Optional
from langchain.embeddings import OpenAIEmbeddings
from chromadb.api.types import Documents, Embeddings
from embedchain.config.apps.BaseAppConfig import BaseAppConfig
from embedchain.models import (Providers, VectorDimensions)
from dotenv import load_dotenv
load_dotenv("deployment.env")

class MyAzureOpenAIAppConfig(BaseAppConfig):
    """
    Config to initialize an embedchain custom `CustomAppConfig` instance that adds embedding_chunk_size=16
    """

    def __init__(
        self,
        embedding_chunk_size=16,
        log_level='DEBUG',
        embedding_fn=None,
        provider=Providers.AZURE_OPENAI,
        db=None,
        host=None,
        port=None,
        id=None,
        collection_name=None,
        deployment_name=None,
        collect_metrics= None,
        db_type= None,
        es_config=None,
    ):
        """
        :param embedding_chunk_size: Optional. (Int) accounts for Azure OPENAI throttling
        :param log_level: Optional. (String) Debug level
        ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'].
        :param embedding_fn: Optional. Embedding function to use.
        :param embedding_fn_model: Optional. Model name to use for embedding function.
        :param db: Optional. (Vector) database to use for embeddings.
        :param host: Optional. Hostname for the database server.
        :param port: Optional. Port for the database server.
        :param id: Optional. ID of the app. Document metadata will have this id.
        :param collection_name: Optional. Collection name for the database.
        :param open_source_app_config: Optional. Config instance needed for open source apps.
        :param collect_metrics: Defaults to True. Send anonymous telemetry to improve embedchain.
        :param db_type: Optional. type of Vector database to use.
        :param es_config: Optional. elasticsearch database config to be used for connection
        """
        if provider:
            self.provider=provider

        super().__init__(
            log_level=log_level,
            embedding_fn=MyAzureOpenAIAppConfig.my_embedding_function(
                deployment_name=deployment_name,
                embedding_chunk_size = embedding_chunk_size
            ),
            db=db,
            host=host,
            port=port,
            id=id,
            collection_name=collection_name,
            collect_metrics=collect_metrics,
            db_type=db_type,
            vector_dim=VectorDimensions.OPENAI.value,
            es_config=es_config,
        )

    @staticmethod
    def langchain_default_concept(embeddings: Any):
        """
        Langchains default function layout for embeddings.
        """

        def embed_function(texts: Documents) -> Embeddings:
            return embeddings.embed_documents(texts)

        return embed_function

    @staticmethod
    def my_embedding_function(deployment_name: str = None,
                              embedding_chunk_size=None
                              ):
      if deployment_name:
          embeddings = OpenAIEmbeddings(deployment=deployment_name, chunk_size=embedding_chunk_size)
      else:
          embeddings = OpenAIEmbeddings(chunk_size=embedding_chunk_size)
      return MyAzureOpenAIAppConfig.langchain_default_concept(embeddings)