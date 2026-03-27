from dataclasses import dataclass

from langchain_huggingface import HuggingFaceEndpointEmbeddings, HuggingFaceEmbeddings

from app.repositories import *


@dataclass
class MetaClientManger:
    dw_repository: DWMysqlRepository
    meta_repository: MetaMysqlRepository
    embedding_client: HuggingFaceEndpointEmbeddings | HuggingFaceEmbeddings
    metric_qdrant_repository: MetricQdrantRepository
    column_qdrant_repository: ColumnQdrantRepository
    full_text_repository: ValueESRepository
