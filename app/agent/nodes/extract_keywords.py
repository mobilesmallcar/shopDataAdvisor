import jieba.analyse
from langgraph.runtime import Runtime

from app.agent.state import DataAgentState
from app.core.base_log import logger


def is_numeric(s: str) -> bool:
    try:
        float(s)
        return True
    except (ValueError, TypeError):
        return False


async def extract_keywords(state: DataAgentState, runtime: Runtime[DataAgentState]):
    writer = runtime.stream_writer
    writer("提取关键字")
