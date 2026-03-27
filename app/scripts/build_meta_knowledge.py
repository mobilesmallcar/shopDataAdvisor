import asyncio
from argparse import ArgumentParser

from pathlib import Path

from app.schemas import MetaClientManger
from app.decorators import with_meta_clients
from app.service import MetaKnowledgeService


@with_meta_clients
async def build(client_manager: MetaClientManger, meta_config: Path):
    # 1. 获取service
    service = MetaKnowledgeService(client_manager)
    # 2. 清除残留数据
    await service.delete_data(meta_config)
    # 3. 构建元数据
    await service.build_meta_knowledge(meta_config)


if __name__ == '__main__':
    """解析命令行参数"""
    parser = ArgumentParser()
    parser.add_argument('-c', '--config', required=True)
    args = parser.parse_args()
    # 调用执行器
    asyncio.run(build(Path(args.config)))
