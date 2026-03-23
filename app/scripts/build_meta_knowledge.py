import asyncio
from argparse import ArgumentParser

from pathlib import Path

from app.client.mysql_client_manager import dw_client_manager, meta_client_manager, MySQLClientManager
from app.core.base_log import logger
from app.repositories.mysql.dw_mysql_repository import DWMysqlRepository
from app.repositories.mysql.meta_mysql_repository import MetaMysqlRepository
from app.schemas.meta_client_manager_schemas import MetaClientManger
from app.service.meta_knowledge_service import MetaKnowledgeService


async def build(meta_config: Path):
    try:
        # 1.客户端的初始化
        logger.info("管理器初始化中...")
        dw_client_manager.init()
        meta_client_manager.init()

        # 2. 构建客户端管理器
        async with (
            dw_client_manager.session_factory() as dw_session,
            meta_client_manager.session_factory() as meta_session
        ):
            client_manager = MetaClientManger(
                dw_repository=DWMysqlRepository(dw_session),
                meta_repository=MetaMysqlRepository(meta_session)
            )

            # 3. 调用构建元数据的service
            service = MetaKnowledgeService(client_manager)

            # 4. 调用方法
            await service.build_meta_knowledge(meta_config)

    finally:
        await dw_client_manager.close()
        await meta_client_manager.close()


if __name__ == '__main__':
    """解析命令行参数"""
    parser = ArgumentParser()
    parser.add_argument('-c', '--config', required=True)
    args = parser.parse_args()
    # 调用执行器
    asyncio.run(build(Path(args.config)))
