from langgraph.runtime import Runtime

from app.agent.state import DataAgentState
from app.agent.context import DataAgentContext
from app.decorators import llm_invoke

# 导入模型
from app.models.es.value_info_es import ValueInfoES
# 导入仓库
from app.repositories.es.value_es_repository import ValueESRepository
# 导入装饰器
from app.decorators import recall_node


# 仓库搜索相关信息
async def search_value(
        repo: ValueESRepository,
        keyword: str,
        score: float,
        limit: int
) -> list[ValueInfoES]:
    return await repo.query(keyword, score, limit)


@llm_invoke(
    prompt_name="extend_keywords_for_value_recall",
    param_builder=lambda state: {
        "query": state.query,
    }
)
@recall_node(
    repo_getter=lambda runtime: runtime.context.client_manager.full_text_repository,
    search_func=search_value,
    model_cls=ValueInfoES,
    need_embedding=False,
    display_name="字段值"
)
async def recall_value(state: DataAgentState, runtime: Runtime[DataAgentContext],
                       values_map: dict[str, ValueInfoES]):
    return {"retrieved_values": list(values_map.values())}
