from typing import Optional

from pydantic import BaseModel

# 导入客户端管理
from app.schemas import MetaClientManger


class DataAgentContext(BaseModel):
    client_manager: Optional[MetaClientManger] = None

    # ✅强制允许任意类型！
    model_config = {"arbitrary_types_allowed": True}
