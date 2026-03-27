from typing import TypeVar, Callable, Awaitable, List, Dict
from pprint import pformat

from langgraph.runtime import Runtime
from langchain_huggingface import HuggingFaceEmbeddings

from app.core import logger
from app.agent.state import DataAgentState
from app.agent.context import DataAgentContext

# 模型导入
from app.models import ColumnInfoQdrant, MetricInfoQdrant, ValueInfoES

# 仓库导入
from app.repositories import ColumnQdrantRepository, MetricQdrantRepository, ValueESRepository

T = TypeVar("T", bound=ValueInfoES | ColumnInfoQdrant | MetricInfoQdrant)
Repo = TypeVar("Repo", bound=ColumnQdrantRepository | MetricQdrantRepository | ValueESRepository)


# --------------------------
#  通用召回节点装饰器
# --------------------------
def recall_node(
        repo_getter: Callable[[Runtime[DataAgentContext]], Repo],
        search_func: Callable,
        model_cls: type[T],
        need_embedding: bool = False,
        display_name: str = ""
):
    def decorator(func: Callable[[DataAgentState, Runtime[DataAgentContext], Dict[str, T]], Awaitable[dict]]):
        async def wrapper(state: DataAgentState, runtime: Runtime[DataAgentContext], llm_result: list[str]) -> dict:
            # writer = runtime.stream_writer
            # writer({"process": f"召回{display_name}"})

            # retrieved_key = f"retrieved_{model_cls.__name__.lower()}"
            # query = state.query
            keywords = state.keywords
            repo = repo_getter(runtime)

            logger.debug(f"召回{display_name}keywords: {keywords}")
            logger.debug(f"召回{display_name}大模型抽取的关键字参数{llm_result}")
            keywords = list(set(keywords + llm_result))
            logger.debug(f"召回{display_name}合并后参数{keywords}")
            # 获取 embedding（如果需要）
            embedding = None
            if need_embedding:
                embedding = runtime.context.client_manager.embedding_client

            # 召回并去重
            data_map: Dict[str, T] = {}
            for keyword in keywords:
                if need_embedding:
                    # 搜索qdrant
                    items = await search_func(repo, keyword, 0.6, 5, embedding)
                else:
                    # 搜索ES
                    items = await search_func(repo, keyword, 0.6, 5)

                for item in items:
                    if item.id not in data_map:
                        data_map[item.id] = item

            logger.info(f"[{display_name}]召回成功:{pformat(data_map.keys(), indent=2)}")
            return await func(state, runtime, data_map)

        return wrapper

    return decorator
