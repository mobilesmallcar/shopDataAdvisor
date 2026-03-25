from typing import TypeVar, Callable, Awaitable, List, Dict
from pprint import pformat

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime
from langchain_huggingface import HuggingFaceEmbeddings

from app.core.base_log import logger
from app.agent.llm import llm_client
from app.agent.state import DataAgentState
from app.agent.context import DataAgentContext
from app.prompt.prompt_loader import load_prompt

# 模型导入
from app.models.qdrant.column_info_qdrant import ColumnInfoQdrant
from app.models.qdrant.metric_info_qdrant import MetricInfoQdrant
from app.models.es.value_info_es import ValueInfoES

# 仓库导入
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository
from app.repositories.es.value_es_repository import ValueESRepository

T = TypeVar("T")
Repo = TypeVar("Repo")


# --------------------------
# 1. 仓库获取器（从 runtime 中获取对应仓库）
# --------------------------
def get_column_repo(runtime: Runtime[DataAgentContext]) -> ColumnQdrantRepository:
    return runtime.context.client_manager.column_qdrant_repository


def get_metric_repo(runtime: Runtime[DataAgentContext]) -> MetricQdrantRepository:
    return runtime.context.client_manager.metric_qdrant_repository


def get_value_repo(runtime: Runtime[DataAgentContext]) -> ValueESRepository:
    return runtime.context.client_manager.full_text_repository


# --------------------------
# 2. 具体搜索函数
# --------------------------
async def search_column(
        repo: ColumnQdrantRepository,
        keyword: str,
        score: float,
        limit: int,
        embedding: HuggingFaceEmbeddings
) -> List[ColumnInfoQdrant]:
    vec = await embedding.aembed_query(keyword)
    return await repo.search(vec, score, limit)


async def search_metric(
        repo: MetricQdrantRepository,
        keyword: str,
        score: float,
        limit: int,
        embedding: HuggingFaceEmbeddings
) -> List[MetricInfoQdrant]:
    vec = await embedding.aembed_query(keyword)
    return await repo.search(vec, score, limit)


async def search_value(
        repo: ValueESRepository,
        keyword: str,
        score: float,
        limit: int
) -> List[ValueInfoES]:
    return await repo.query(keyword, score, limit)


# --------------------------
# 3. 通用召回节点装饰器
# --------------------------
def recall_node(
        prompt_name: str,
        repo_getter: Callable[[Runtime[DataAgentContext]], Repo],
        search_func: Callable,
        model_cls: type[T],
        need_embedding: bool = False,
        display_name: str = ""
):
    def decorator(func: Callable[[DataAgentState, Runtime[DataAgentContext], Dict[str, T]], Awaitable[dict]]):
        async def wrapper(state: DataAgentState, runtime: Runtime[DataAgentContext]) -> dict:
            writer = runtime.stream_writer
            writer(f"召回{display_name}")

            retrieved_key = f"retrieved_{model_cls.__name__.lower()}"
            query = state.query
            keywords = state.keywords
            repo = repo_getter(runtime)

            try:
                # 构建链
                prompt = PromptTemplate(
                    template=load_prompt(prompt_name),
                    input_variables=["query"]
                )
                chain = prompt | llm_client | JsonOutputParser()

                # 大模型扩展关键词
                result_content = await chain.ainvoke({"query": query})
                logger.debug(f"召回{display_name}keywords: {keywords}")
                logger.debug(f"召回{display_name}大模型抽取的关键字参数{result_content}")
                keywords = list(set(keywords + result_content))
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

            except Exception as e:
                logger.error(f"[{display_name}]召回失败: {str(e)}")
                return {retrieved_key: []}

        return wrapper

    return decorator
