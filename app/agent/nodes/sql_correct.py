from typing import Any

from langgraph.runtime import Runtime

from app.agent.nodes.decorator_utils.llm_utils import llm_invoke
from app.agent.state import DataAgentState
from app.agent.context import DataAgentContext
from app.core.base_log import logger


def build_correct_sql_params(state: DataAgentState) -> dict[str, Any]:
    return {
        "query": state.query,
        "metric_infos": state.metric_infos,
        "table_infos": state.table_infos,
        "date_info": state.date_info,
        "db_info": state.db_info,
        "sql": state.sql,
        "error": state.error
    }


@llm_invoke(
    prompt_name="correct_sql",
    param_builder=build_correct_sql_params,
)
async def correct_sql(state: DataAgentState, runtime: Runtime[DataAgentContext], result: str):
    writer = runtime.stream_writer
    writer("SQL纠正")

    # 返回
    logger.info(f"SQL纠正结果：{result}")
    return {"sql": result, "error": None}
