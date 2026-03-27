from langgraph.runtime import Runtime

from app.agent.state import DataAgentState
from app.agent.context import DataAgentContext
from app.core.base_log import logger


async def execute_sql(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer("SQL执行")

    # 1. 获取参数
    sql = state.sql
    dw_repository = runtime.context.client_manager.dw_repository

    # 2. 执行SQL
    try:
        result = await dw_repository.execute_sql(sql)
        logger.info(f"SQL执行成功: {result}")
        writer({"result": result})
        return {"result": result}
    except Exception as e:
        logger.error(f"SQL执行失败: {str(e)}")
        return {"error": str(e)}
