from typing import Optional

from pydantic import BaseModel


class DataAgentState(BaseModel):
    query: str  # 查询

    keywords: list[str] = []  # 关键词列表，由query分词和LLM生成得到，用于召回信息
    error: Optional[str] = None
