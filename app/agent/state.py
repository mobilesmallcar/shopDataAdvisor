from typing import Optional

from pydantic import BaseModel

from app.models.es.value_info_es import ValueInfoES
from app.models.qdrant.column_info_qdrant import ColumnInfoQdrant
from app.models.qdrant.metric_info_qdrant import MetricInfoQdrant


class DataAgentState(BaseModel):
    query: str  # 查询

    keywords: list[str] = []  # 关键词列表，由query分词和LLM生成得到，用于召回信息
    error: Optional[str] = None

    retrieved_columns: list[ColumnInfoQdrant] = []
    retrieved_metrics: list[MetricInfoQdrant] = []
    retrieved_values: list[ValueInfoES] = []