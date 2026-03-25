from pydantic import ConfigDict, BaseModel


class ValueInfoES(BaseModel):
    id: str
    value: str
    type: str
    column_id: str
    column_name: str
    table_id: str
    table_name: str

    model_config = ConfigDict(
        from_attributes=True,  # 关键！允许直接从 SQLAlchemy 对象读取属性
        extra="ignore",  # 忽略 SQLAlchemy 内部属性（如 _sa_instance_state）
    )
