from pprint import pformat

from langgraph.runtime import Runtime

from app.core.base_log import logger
from app.agent.state import DataAgentState
from app.agent.context import DataAgentContext
from app.models.es.value_info_es import ValueInfoES
from app.models.qdrant.column_info_qdrant import ColumnInfoQdrant
from app.models.qdrant.metric_info_qdrant import MetricInfoQdrant


async def merge_retrieved_info(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer("合并召回信息")

    # 1. 获取需要合并的对象
    retrieved_columns: list[ColumnInfoQdrant] = state.retrieved_columns
    retrieved_metrics: list[MetricInfoQdrant] = state.retrieved_metrics
    retrieved_values: list[ValueInfoES] = state.retrieved_values

    logger.debug(f"需要合并的对象:\n{pformat(retrieved_values, indent=2)}")
    logger.debug(f"需要合并的对象:\n{pformat(retrieved_metrics, indent=2)}")
    logger.debug(f"需要合并的对象:\n{pformat(retrieved_columns, indent=2)}")



