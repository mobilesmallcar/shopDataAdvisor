from sqlalchemy import text

from app.config.config_loader import load_config
from app.config.meta_config import MetaConfig, TableConfig
from app.core.base_log import logger
from app.models.mysql.column_info_mysql import ColumnInfoMySQL
from app.models.mysql.table_info_mysql import TableInfoMySQL
from app.schemas.meta_client_manager_schemas import MetaClientManger


class MetaKnowledgeService:

    def __init__(self, client_manager: MetaClientManger):
        self.client_manager = client_manager

    async def build_meta_knowledge(self, config_file):
        # 1.加载配置文件
        meta_config: MetaConfig = load_config(MetaConfig, config_file)
        logger.info('加载元数据配置文件')
        if meta_config.tables:
            # 2.保存表信息到meta数据库
            table_infos, column_infos = await self._save_tables_to_meta_db(meta_config.tables)
            logger.info('保存表信息和字段信息到meta数据库')
            # 3.同步字段信息到qdrant
            await self._sync_columns_to_qdrant(column_infos)
            logger.info('同步字段信息到qdrant')
            # # 4.同步字段数据到es
            # await self._sync_values_to_es(table_infos, column_infos, meta_config)
            # logger.info('同步字段值到es')
        if meta_config.metrics:
            pass
            # # 3.保存metrics信息到meta数据库
            # metric_infos = await self._save_metrics_to_meta_db(meta_config.metrics)
            # logger.info('保存metric信息到meta数据库')
            #
            # # 6.同步metric信息到qdrant
            # await self._sync_metrics_to_qdrant(metric_infos)
            # logger.info('同步metric信息到qdrant')
        logger.info('元数据知识库构建完成')

    async def _save_tables_to_meta_db(self, tables: list[TableConfig]) \
            -> tuple[list[TableInfoMySQL], list[ColumnInfoMySQL]]:
        table_infos = []
        column_infos = []

        # 1. 构建表和列信息
        for table in tables:
            # 获取表id
            table_id = table.name

            # 1.1 构建表信息
            table_infos.append(TableInfoMySQL(
                id=table_id,
                name=table.name,
                role=table.role,
                description=table.description
            ))

            # 1.2 构建列信息
            # a) 获取字段类型映射<字段名:字段类型>
            column_types = await self.client_manager.dw_repository.get_column_types(table.name)

            for column in table.columns:
                # b) 获取字段值映射<字段名:字段值>
                column_values: list \
                    = await self.client_manager.dw_repository.get_column_values(table.name, column.name, 10)
                # c) 构建列信息
                column_info = ColumnInfoMySQL(
                    id=f"{table_id}.{column.name}",
                    name=column.name,
                    type=column_types[column.name],
                    role=column.role,
                    examples=column_values,
                    description=column.description,
                    alias=column.alias,
                    table_id=table_id
                )
                # d) 存入column_infos
                column_infos.append(column_info)

        # 2. 保存元数据信息存入到meta.[table_info & column_info]
        meta_repository = self.client_manager.meta_repository
        async with meta_repository.meta_session.begin():
            await meta_repository.meta_session.execute(text("DELETE FROM column_info"))
            await meta_repository.meta_session.execute(text("DELETE FROM table_info"))
            await meta_repository.save_table_infos(table_infos)
            await meta_repository.save_column_infos(column_infos)

        # 3. 返回
        return table_infos, column_infos

    # async def _sync_columns_to_qdrant(self, column_infos):
    #     # 创建qdrant collection
    #     await self.column_qdrant_repository.ensure_collection()
