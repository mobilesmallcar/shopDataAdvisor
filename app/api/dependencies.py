from fastapi import Depends
from langgraph.graph.state import CompiledStateGraph

from app.agent.graph import graph_app

# 导入客户端
from app.client import *
# 导入仓库
from app.repositories import *
# 导入管理器
from app.schemas import MetaClientManger
# 导入service
from app.service import ChatService


# 获取 Meta session
async def _get_meta_session():
    async with meta_client_manager.session_factory() as session:
        yield session


# 获取 DW session
async def _get_dw_session():
    async with dw_client_manager.session_factory() as session:
        yield session


# 构建客户端管理器
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


# 构建
async def _get_graph():
    return graph_app


async def get_chat_service(
        graph: CompiledStateGraph = Depends(_get_graph),
        client_manager: MetaClientManger = Depends(_get_client_manager)
) -> ChatService:
    # 创建服务实例
    return ChatService(graph=graph, client_manager=client_manager)
