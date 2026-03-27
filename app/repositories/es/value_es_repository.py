from elasticsearch import AsyncElasticsearch

from app.core import logger
from app.models import ValueInfoES
from elasticsearch.helpers import async_bulk


class ValueESRepository:
    es_index_name = "data_advisor_v1"
    es_index_mapping = {
        "properties": {
            "id": {"type": "keyword"},
            "value": {"type": "text", "analyzer": "ik_max_word", "search_analyzer": "ik_max_word"},
            "type": {"type": "keyword"},
            "column_id": {"type": "keyword"},
            "column_name": {"type": "keyword"},
            "table_id": {"type": "keyword"},
            "table_name": {"type": "keyword"},
        }
    }

    def __init__(self, es_client: AsyncElasticsearch):
        self.es_client = es_client

    async def delete_index(self):
        exists = await self.es_client.indices.exists(index=self.es_index_name)
        if exists:
            logger.debug(f"[ElasticSearch]索引[{self.es_index_name}]已删除")
            await self.es_client.indices.delete(index=self.es_index_name)
        else:
            logger.debug(f"[ElasticSearch]索引[{self.es_index_name}]不存在,不执行删除,返回..")

    async def ensure_index(self):
        exists = await self.es_client.indices.exists(index=self.es_index_name)
        # 存在则先删除
        if not exists:
            # 创建索引，传入 mapping
            await self.es_client.indices.create(
                index=self.es_index_name,
                mappings=self.es_index_mapping  # 传入你的字段映射
            )
            logger.debug(f"[ElasticSearch]索引[{self.es_index_name}]已创建")
        else:
            logger.debug(f"[ElasticSearch]索引[{self.es_index_name}]已存在,返回..")

    async def batch_index(self, docs: list[ValueInfoES], batch_size: int = 10):
        if not docs:
            return

        def generate_actions():
            for doc in docs:
                yield {
                    "_op_type": "index",  # 存在则更新，不存在则创建
                    "_index": self.es_index_name,
                    "_id": doc.id,  # 用 id 字段作为 ES 文档 ID（TypedDict 用 doc["id"]，dataclass 用 doc.id）
                    "_source": doc.model_dump()  # 直接传入你的 ValueInfoES 对象
                }

        # 执行批量插入
        success, failed = await async_bulk(
            client=self.es_client,
            actions=generate_actions(),
            chunk_size=batch_size,
            refresh=True  # 插入后立即刷新索引（生产环境可关闭）
        )
        logger.debug(f"批量插入成功：{success} 条，失败：{len(failed)} 条")
        if failed:
            logger.warning("失败详情：", failed)

    async def query(self, query: str, score_threshold: float = 0.6, limit: int = 10) -> list[ValueInfoES]:
        es_query = {
            "match": {
                "value": query
            }
        }
        resp = await self.es_client.search(
            index=self.es_index_name,
            query=es_query,
            min_score=score_threshold,
            size=limit,
        )
        hits = resp.get("hits", {}).get("hits", {})

        results: list[ValueInfoES] = []
        for hit in hits:
            source = hit.get("_source")
            results.append(ValueInfoES(**source))

        return results


if __name__ == '__main__':
    import asyncio
    from app.schemas.meta_client_manager_schemas import MetaClientManger
    from app.decorators.meta_client_manager_utils import with_meta_clients


    @with_meta_clients
    async def main(client_manager: MetaClientManger):
        value_infos = ['统计华北地区的销售总额', '销售总额', '统计', '华北地区']
        for info in value_infos:
            result = await client_manager.full_text_repository.query(
                query=info
            )
            print(result)

    asyncio.run(main())
