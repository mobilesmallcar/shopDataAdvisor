import asyncio

from langgraph.runtime import Runtime

from app.agent.state import DataAgentState


async def recall_value(state: DataAgentState, runtime: Runtime[DataAgentState]):
    writer = runtime.stream_writer
    writer('召回值...')
    await asyncio.sleep(1)