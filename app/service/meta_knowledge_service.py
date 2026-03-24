import uuid

from sqlalchemy import text

from app.config.config_loader import load_config
from app.config.meta_config import MetaConfig, TableConfig
from app.core.base_log import logger
from app.models.es.value_info_es import ValueInfoES
from app.models.mysql.column_info_mysql import ColumnInfoMySQL
from app.models.mysql.table_info_mysql import TableInfoMySQL
from app.models.qdrant.column_info_qdrant import ColumnInfoQdrant
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
            # 4.同步字段数据到es
            await self._sync_values_to_es(table_infos, column_infos, meta_config)
            logger.info('同步字段值到es')
        if meta_config.metrics:
            # 3.保存metrics信息到meta数据库
            metric_infos = await self._save_metrics_to_meta_db(meta_config.metrics)
            logger.info('保存metric信息到meta数据库')
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
                    id=f"{table.name}.{column.name}",
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

    async def _sync_columns_to_qdrant(self, columns: list[ColumnInfoMySQL]):
        # 1. 创建qdrant collection
        await self.client_manager.column_qdrant_repository.ensure_collection()

        # 2. 构建qdrant数据
        ids: list = []
        embedding_texts: list[str] = []
        payloads: list[ColumnInfoQdrant] = []
        for column_info in columns:
            # a) 获取payload
            payload = ColumnInfoQdrant.model_validate(column_info)
            # b) 获取需要插入的字段
            fields_values = [column_info.name, column_info.description] + column_info.alias
            # c) 获取需要处理的字段数量
            fields_len = len(fields_values)

            # d) 构建所需对象
            ids.extend([uuid.uuid4() for _ in range(fields_len)])
            payloads.extend([payload for _ in range(fields_len)])

            for field_val in fields_values:
                embedding_texts.append(field_val)
        # 3. 批量嵌入向量
        embeddings = []
        embedding_batch_size = 20
        for i in range(0, len(embedding_texts), embedding_batch_size):
            batch_record_text = embedding_texts[i:i + embedding_batch_size]
            batch_embeddings = await self.client_manager.embedding_client.aembed_documents(batch_record_text)
            embeddings.extend(batch_embeddings)

        # 3. 批量更新qdrant
        await self.client_manager.column_qdrant_repository.upsert(ids, embeddings, payloads, 64)

    async def _sync_values_to_es(
            self,
            table_infos: list[TableInfoMySQL],
            column_infos: list[ColumnInfoMySQL],
            meta_config: MetaConfig
    ):
        # 1. 确保es index 存在
        await self.client_manager.full_text_repository.ensure_index(delete_flag=True)

        values: list[ValueInfoES] = []
        # 2. 构建map对象 表名映射<table_id,table_name> 同步映射<column_id,sync>
        table_id2name = {table_info.id: table_info.name for table_info in table_infos}
        column_id2sync = {}
        for table in meta_config.tables:
            for column in table.columns:
                if column.sync:
                    column_id2sync[f"{table.name}.{column.name}"] = column.sync
        # 3. 构建批量插入对象->ValueInfoES
        for column_info in column_infos:
            table_name = table_id2name[column_info.table_id]
            column_name = column_info.name
            sync = column_id2sync[column_info.id]
            if sync:
                # a) 获取字段值
                column_value: list \
                    = await self.client_manager.dw_repository.get_column_values(table_name, column_name, (1 << 16))
                values.extend([
                    ValueInfoES(
                        id=f"{table_name}.{column_name}.{value}",
                        value=value,
                        type=column_info.type,
                        column_id=column_info.id,
                        column_name=column_name,
                        table_id=column_info.table_id,
                        table_name=table_name
                    ) for value in column_value
                ])
        # 4. 批量插入
        await self.client_manager.full_text_repository.batch_index(values)

    async def _save_metrics_to_meta_db(self, metrics):
        pass
