from langgraph.runtime import Runtime

from app.core import logger
from app.agent.state import DataAgentState
from app.agent.context import DataAgentContext
from app.decorators import writer_node


@writer_node("SQL执行")
async def execute_sql(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    # writer({"process": "SQL执行"})

    # 1. 获取参数
    sql = state.sql
    dw_repository = runtime.context.client_manager.dw_repository

    # 2. 执行SQL
    try:
        result = await dw_repository.execute_sql(sql)
        logger.info(f"SQL执行成功: {result}")
        # writer({"result": result})
        writer({"type": "result", "data": result})
        return {"result": result}
    except Exception as e:
        logger.error(f"SQL执行失败: {str(e)}")
        return {"error": str(e)}
