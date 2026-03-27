from fastapi import Depends
from langgraph.graph.state import CompiledStateGraph

from app.agent.graph import graph_app
from app.client.embedding_client import embedding_client_manager
from app.client.es_client_manager import es_client_manager
from app.client.mysql_client_manager import dw_client_manager, meta_client_manager
from app.client.qdrant_client_manager import qdrant_client_manager
from app.repositories.es.value_es_repository import ValueESRepository
from app.repositories.mysql.dw_mysql_repository import DWMysqlRepository
from app.repositories.mysql.meta_mysql_repository import MetaMysqlRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository
from app.schemas.meta_client_manager_schemas import MetaClientManger
from app.service.chat_service import ChatService


# 获取 Meta session
async def _get_meta_session():
    async with meta_client_manager.session_factory() as session:
        yield session


# 获取 DW session
async def _get_dw_session():
    async with dw_client_manager.session_factory() as session:
        yield session


async def _get_client_manager(
        dw_session=Depends(_get_dw_session),
        meta_session=Depends(_get_meta_session),
):
    return MetaClientManger(
        dw_repository=DWMysqlRepository(dw_session),
        meta_repository=MetaMysqlRepository(meta_session),
        embedding_client=embedding_client_manager.client,
        metric_qdrant_repository=MetricQdrantRepository(qdrant_client_manager.client),
        column_qdrant_repository=ColumnQdrantRepository(qdrant_client_manager.client),
        full_text_repository=ValueESRepository(es_client_manager.client),
    )


async def _get_graph():
    return graph_app


async def get_chat_service(
        graph: CompiledStateGraph = Depends(_get_graph),
        client_manager: MetaClientManger = Depends(_get_client_manager)
) -> ChatService:
    # 创建服务实例
    return ChatService(graph=graph, client_manager=client_manager)


