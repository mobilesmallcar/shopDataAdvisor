from dataclasses import dataclass

from langchain_huggingface import HuggingFaceEndpointEmbeddings, HuggingFaceEmbeddings

from app.repositories.es.value_es_repository import ValueESRepository
from app.repositories.mysql.dw_mysql_repository import DWMysqlRepository
from app.repositories.mysql.meta_mysql_repository import MetaMysqlRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository


@dataclass
class MetaClientManger:
    dw_repository: DWMysqlRepository
    meta_repository: MetaMysqlRepository
    embedding_client: HuggingFaceEndpointEmbeddings | HuggingFaceEmbeddings
    metric_qdrant_repository: MetricQdrantRepository
    column_qdrant_repository: ColumnQdrantRepository
    full_text_repository: ValueESRepository
