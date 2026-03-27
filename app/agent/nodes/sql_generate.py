from typing import Any
from langgraph.runtime import Runtime

from app.core import logger
from app.agent.state import DataAgentState
from app.agent.context import DataAgentContext

# 导入装饰器
from app.decorators import llm_invoke, writer_node


def build_generate_sql_params(state: DataAgentState) -> dict[str, Any]:
    return {
        "query": state.query,
        "metric_infos": state.metric_infos,
        "table_infos": state.table_infos,
        "date_info": state.date_info,
        "db_info": state.db_info
    }


@writer_node("SQL生成")
@llm_invoke(
    prompt_name="generate_sql",
    param_builder=build_generate_sql_params,
    enable_text=True
)
async def generate_sql(state: DataAgentState, runtime: Runtime[DataAgentContext], result: str):
    writer = runtime.stream_writer
    writer({"process": "SQL生成"})

    # 返回
    logger.info(f"SQL生成结果：{result}")
    return {"sql": result}
