from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.nodes.decorator_utils.recall_utils import recall_node, get_column_repo, search_column
from app.agent.state import DataAgentState
from app.models.qdrant.column_info_qdrant import ColumnInfoQdrant


@recall_node(
    prompt_name="extend_keywords_for_column_recall",
    repo_getter=get_column_repo,
    search_func=search_column,
    model_cls=ColumnInfoQdrant,
    need_embedding=True,
    display_name="字段信息"
)
async def recall_column(state: DataAgentState, runtime: Runtime[DataAgentContext],
                        columns_map: dict[str, ColumnInfoQdrant]):
    return {"retrieved_columns": list(columns_map.values())}
