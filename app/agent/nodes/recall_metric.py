from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.nodes.decorator_utils.llm_utils import llm_invoke
from app.agent.nodes.decorator_utils.recall_utils import recall_node, get_metric_repo, search_metric
from app.agent.state import DataAgentState
from app.models.qdrant.metric_info_qdrant import MetricInfoQdrant


@llm_invoke(
    prompt_name="extend_keywords_for_metric_recall",
    param_builder=lambda state: {
        "query": state.query,
    }
)
@recall_node(
    repo_getter=get_metric_repo,
    search_func=search_metric,
    model_cls=MetricInfoQdrant,
    need_embedding=True,
    display_name="指标信息"
)
async def recall_metric(state: DataAgentState, runtime: Runtime[DataAgentContext],
                        metrics_map: dict[str, MetricInfoQdrant]):
    return {"retrieved_metrics": list(metrics_map.values())}
