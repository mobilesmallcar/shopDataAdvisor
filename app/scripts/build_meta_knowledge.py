import asyncio
from argparse import ArgumentParser

from pathlib import Path

from app.client.embedding_client import embedding_client_manager
from app.client.es_client_manager import es_client_manager
from app.client.mysql_client_manager import dw_client_manager, meta_client_manager, MySQLClientManager
from app.client.qdrant_client_manager import qdrant_client_manager
from app.core.base_log import logger
from app.repositories.es.value_es_repository import ValueESRepository
from app.repositories.mysql.dw_mysql_repository import DWMysqlRepository
from app.repositories.mysql.meta_mysql_repository import MetaMysqlRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository
from app.schemas.meta_client_manager_schemas import MetaClientManger
from app.service.meta_knowledge_service import MetaKnowledgeService


async def build(meta_config: Path):
    try:
        # 1.客户端的初始化
        logger.info("管理器初始化中...")
        dw_client_manager.init()
        meta_client_manager.init()
        embedding_client_manager.init()
        qdrant_client_manager.init()
        es_client_manager.init()

        # 2. 构建客户端管理器
        async with (
            dw_client_manager.session_factory() as dw_session,
            meta_client_manager.session_factory() as meta_session
        ):
            # a) 构建需要的对象
            column_qdrant_repository = ColumnQdrantRepository(qdrant_client_manager.client)
            metric_qdrant_repository = MetricQdrantRepository(qdrant_client_manager.client)
            full_text_repository = ValueESRepository(es_client_manager.client)
            # b) 构建manager
            client_manager = MetaClientManger(
                dw_repository=DWMysqlRepository(dw_session),
                meta_repository=MetaMysqlRepository(meta_session),
                embedding_client=embedding_client_manager.client,
                metric_qdrant_repository=metric_qdrant_repository,
                column_qdrant_repository=column_qdrant_repository,
                full_text_repository=full_text_repository,

            )

            # 3. 调用构建元数据的service
            service = MetaKnowledgeService(client_manager)

            # 4. 调用方法
            await service.build_meta_knowledge(meta_config)

    finally:
        await dw_client_manager.close()
        await meta_client_manager.close()
        await qdrant_client_manager.close()
        await es_client_manager.close()


if __name__ == '__main__':
    """解析命令行参数"""
    parser = ArgumentParser()
    parser.add_argument('-c', '--config', required=True)
    args = parser.parse_args()
    # 调用执行器
    asyncio.run(build(Path(args.config)))
