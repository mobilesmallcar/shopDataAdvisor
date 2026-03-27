from langchain_huggingface import HuggingFaceEmbeddings
from langgraph.runtime import Runtime

from app.agent.state import DataAgentState
from app.agent.context import DataAgentContext

# 导入模型
from app.models import ColumnInfoQdrant
# 导入仓库
from app.repositories import ColumnQdrantRepository
# 导入装饰器
from app.decorators import recall_node, llm_invoke, writer_node


# 仓库搜索相关信息
async def search_column(
        repo: ColumnQdrantRepository,
        keyword: str,
        score: float,
        limit: int,
        embedding: HuggingFaceEmbeddings
) -> list[ColumnInfoQdrant]:
    vec = await embedding.aembed_query(keyword)
    return await repo.search(vec, score, limit)


@writer_node("召回字段信息")
@llm_invoke(
    prompt_name="extend_keywords_for_column_recall",
    param_builder=lambda state: {
        "query": state.query,
    }
)
@recall_node(
    repo_getter=lambda runtime: runtime.context.client_manager.column_qdrant_repository,
    search_func=search_column,
    model_cls=ColumnInfoQdrant,
    need_embedding=True,
    display_name="字段信息"
)
async def recall_column(state: DataAgentState, runtime: Runtime[DataAgentContext],
                        columns_map: dict[str, ColumnInfoQdrant]):
    return {"retrieved_columns": list(columns_map.values())}
