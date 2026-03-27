from langgraph.runtime import Runtime
from langchain_huggingface import HuggingFaceEmbeddings

from app.agent.state import DataAgentState
from app.agent.context import DataAgentContext
from app.decorators import llm_invoke

# 导入模型
from app.models.qdrant.metric_info_qdrant import MetricInfoQdrant
# 导入仓库
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository
# 导入装饰器
from app.decorators import recall_node, writer_node


# 仓库搜索相关信息
async def search_metric(
        repo: MetricQdrantRepository,
        keyword: str,
        score: float,
        limit: int,
        embedding: HuggingFaceEmbeddings
) -> list[MetricInfoQdrant]:
    vec = await embedding.aembed_query(keyword)
    return await repo.search(vec, score, limit)


@writer_node("召回指标信息")
@llm_invoke(
    prompt_name="extend_keywords_for_metric_recall",
    param_builder=lambda state: {
        "query": state.query,
    }
)
@recall_node(
    repo_getter=lambda runtime: runtime.context.client_manager.metric_qdrant_repository,
    search_func=search_metric,
    model_cls=MetricInfoQdrant,
    need_embedding=True,
    display_name="指标信息"
)
async def recall_metric(state: DataAgentState, runtime: Runtime[DataAgentContext],
                        metrics_map: dict[str, MetricInfoQdrant]):
    return {"retrieved_metrics": list(metrics_map.values())}
