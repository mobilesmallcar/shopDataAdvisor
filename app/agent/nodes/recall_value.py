from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.nodes.decorator_utils.llm_utils import llm_invoke
from app.agent.nodes.decorator_utils.recall_utils import recall_node, get_value_repo, search_value
from app.agent.state import DataAgentState
from app.models.es.value_info_es import ValueInfoES


@llm_invoke(
    prompt_name="extend_keywords_for_value_recall",
    param_builder=lambda state: {
        "query": state.query,
    }
)
@recall_node(
    repo_getter=get_value_repo,
    search_func=search_value,
    model_cls=ValueInfoES,
    need_embedding=False,
    display_name="字段值"
)
async def recall_value(state: DataAgentState, runtime: Runtime[DataAgentContext],
                       values_map: dict[str, ValueInfoES]):
    return {"retrieved_values": list(values_map.values())}
