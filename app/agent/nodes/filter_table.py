import asyncio

from langgraph.runtime import Runtime

from app.agent.state import DataAgentState


async def filter_table_info(state: DataAgentState, runtime: Runtime[DataAgentState]):
    writer = runtime.stream_writer
    writer("过滤表格信息")
    await asyncio.sleep(1)
