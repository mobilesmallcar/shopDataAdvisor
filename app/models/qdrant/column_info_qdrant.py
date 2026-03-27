from typing import Any

from pydantic import ConfigDict, field_validator, BaseModel


class ColumnInfoQdrant(BaseModel):
    id: str
    name: str
    type: str
    role: str
    examples: list[str]
    description: str
    alias: list[str]
    table_id: str

    model_config = ConfigDict(
        from_attributes=True,  # 关键！允许直接从 SQLAlchemy 对象读取属性
        extra="ignore",  # 忽略 SQLAlchemy 内部属性（如 _sa_instance_state）
    )

    @field_validator("examples", "alias", mode="before")
    @classmethod
    def ensure_list_str(cls, v: Any) -> list[str]:
        """把 None、dict、空值统一转为 list[str]"""
        if not v:
            return []
        if isinstance(v, list):
            return [str(item) for item in v]
        if isinstance(v, dict):
            # 根据你的实际业务决定怎么转 dict（这里转所有 value）
            return [str(val) for val in v.values()]
        return [str(v)]
