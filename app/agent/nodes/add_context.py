import asyncio

from langgraph.runtime import Runtime

from app.agent.state import DataAgentState, DateInfoState, DBInfoState
from app.agent.context import DataAgentContext
from datetime import datetime

from app.core.base_log import logger


async def add_context(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer("添加额外上下文")

    # 1. 获取当前时间
    today = datetime.today()

    # 2. 构建时间上下文
    quarter = f"Q{(today.month - 1) // 3 + 1}"
    date_info = DateInfoState(
        date=today.strftime("%Y-%m-%d"),
        weekday=today.strftime("%A"),
        quarter=quarter
    )

    # 3. 构建db 上下文
    db_info = DBInfoState(**await runtime.context.client_manager.dw_repository.get_db_info())

    # 4. 返回
    logger.info(f'添加上下文信息-date_info:{date_info},db_info:{db_info}')
    return {"date_info": date_info, "db_info": db_info}
