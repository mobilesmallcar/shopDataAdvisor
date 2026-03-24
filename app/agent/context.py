from typing import Optional

from pydantic import BaseModel

from app.schemas.meta_client_manager_schemas import MetaClientManger


class DataAgentContext(BaseModel):
    client_manager: Optional[MetaClientManger] = None

    # ✅强制允许任意类型！
    model_config = {"arbitrary_types_allowed": True}
