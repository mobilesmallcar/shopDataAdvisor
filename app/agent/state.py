from typing import Optional, Any

from pydantic import BaseModel, ConfigDict

from app.models.es.value_info_es import ValueInfoES
from app.models.qdrant.column_info_qdrant import ColumnInfoQdrant
from app.models.qdrant.metric_info_qdrant import MetricInfoQdrant


class _BaseInfoState(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,  # 🔥 关键：允许直接传别的模型实例
        extra="ignore",  # 🔥 关键：忽略多余字段
    )


class ColumnInfoState(_BaseInfoState):
    name: str  # 字段名称
    type: str  # 字段类型
    role: str  # 字段角色（primary_key/foreign_key/dimension/measure）
    description: str  # 字段描述
    alias: list[str]  # 字段别名
    examples: list[Any]  # 字段示例


class TableInfoState(_BaseInfoState):
    name: str  # 表名称
    role: str  # 表角色（fact/dim）
    description: str  # 表描述
    columns: list[ColumnInfoState]  # 字段信息


class MetricInfoState(_BaseInfoState):
    name: str  # 指标名称
    description: str  # 指标描述
    alias: list[str]  # 指标别名


class DataAgentState(BaseModel):
    query: str  # 查询

    keywords: list[str] = []  # 关键词列表，由query分词和LLM生成得到，用于召回信息
    error: Optional[str] = None

    # 召回信息
    retrieved_columns: list[ColumnInfoQdrant] = []
    retrieved_metrics: list[MetricInfoQdrant] = []
    retrieved_values: list[ValueInfoES] = []

    # 合并信息
    table_infos: list[TableInfoState] = []
    metric_infos: list[MetricInfoState] = []
