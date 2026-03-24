import asyncio
from argparse import ArgumentParser

from pathlib import Path

from app.schemas.meta_client_manager_schemas import MetaClientManger
from app.service.BaseService import with_meta_clients
from app.service.meta_knowledge_service import MetaKnowledgeService


@with_meta_clients
async def build(client_manager: MetaClientManger, meta_config: Path):
    # 业务代码
    service = MetaKnowledgeService(client_manager)
    await service.delete_data(meta_config)
    await service.build_meta_knowledge(meta_config)


if __name__ == '__main__':
    """解析命令行参数"""
    parser = ArgumentParser()
    parser.add_argument('-c', '--config', required=True)
    args = parser.parse_args()
    # 调用执行器
    asyncio.run(build(Path(args.config)))
