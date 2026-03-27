import asyncio

from langgraph.runtime import Runtime

from app.agent.state import DataAgentState
from app.agent.context import DataAgentContext
from app.core.base_log import logger


async def validate_sql(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer("SQL校验")

    # 1. 获取参数
    sql = state.sql
    dw_repository = runtime.context.client_manager.dw_repository

    # 2. 校验sql
    try:
        # 执行explain
        await dw_repository.validate_sql(sql)
        logger.info(f"[SQL]校验成功")
        return {"sql": sql}
    except Exception as e:
        # 3. 失败返error
        logger.error(f"[SQL]校验失败: {str(e)}")
        return {"error": str(e)}
