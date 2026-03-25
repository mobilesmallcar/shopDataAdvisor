import asyncio

from langgraph.runtime import Runtime

from app.agent.state import DataAgentState
from app.agent.context import DataAgentContext


async def filter_table_info(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer("过滤表格信息")
    await asyncio.sleep(1)
