import asyncio

from langgraph.runtime import Runtime

from app.agent.state import DataAgentState


async def generate_sql(state: DataAgentState, runtime: Runtime[DataAgentState]):
    writer = runtime.stream_writer
    writer("SQL生成")
    await asyncio.sleep(1)