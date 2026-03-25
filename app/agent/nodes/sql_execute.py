import asyncio

from langgraph.runtime import Runtime

from app.agent.state import DataAgentState
from app.agent.context import DataAgentContext


async def execute_sql(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer("SQL执行")
    await asyncio.sleep(1)