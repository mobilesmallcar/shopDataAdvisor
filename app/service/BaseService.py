from pathlib import Path
from functools import wraps

from app.core.base_log import logger
from app.client.es_client_manager import es_client_manager
from app.client.embedding_client import embedding_client_manager
from app.client.qdrant_client_manager import qdrant_client_manager
from app.client.mysql_client_manager import dw_client_manager, meta_client_manager, MySQLClientManager
from app.core.context import request_id_ctx_var
from app.repositories.es.value_es_repository import ValueESRepository
from app.repositories.mysql.dw_mysql_repository import DWMysqlRepository
from app.repositories.mysql.meta_mysql_repository import MetaMysqlRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository
from app.schemas.meta_client_manager_schemas import MetaClientManger


def with_meta_clients(func):
    """
    装饰器：自动初始化所有客户端、管理会话、自动关闭
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            # 如果没有默认值那么默认
            request_id = kwargs.pop("request_id", "xsy")
            request_id_ctx_var.set(request_id)
            # ========== 初始化 ==========
            logger.info("管理器初始化中...")
            dw_client_manager.init()
            meta_client_manager.init()
            embedding_client_manager.init()
            qdrant_client_manager.init()
            es_client_manager.init()

            # ========== 会话 ==========
            async with (
                dw_client_manager.session_factory() as dw_session,
                meta_client_manager.session_factory() as meta_session,
            ):
                # 构建仓库
                column_qdrant_repo = ColumnQdrantRepository(qdrant_client_manager.client)
                metric_qdrant_repo = MetricQdrantRepository(qdrant_client_manager.client)
                full_text_repo = ValueESRepository(es_client_manager.client)

                # 构建全局 client_manager
                client_manager = MetaClientManger(
                    dw_repository=DWMysqlRepository(dw_session),
                    meta_repository=MetaMysqlRepository(meta_session),
                    embedding_client=embedding_client_manager.client,
                    metric_qdrant_repository=metric_qdrant_repo,
                    column_qdrant_repository=column_qdrant_repo,
                    full_text_repository=full_text_repo,
                )

                # ========== 调用业务函数 ==========
                return await func(client_manager, *args, **kwargs)

        finally:
            # ========== 自动关闭 ==========
            await dw_client_manager.close()
            await meta_client_manager.close()
            await qdrant_client_manager.close()
            await es_client_manager.close()

    return wrapper
