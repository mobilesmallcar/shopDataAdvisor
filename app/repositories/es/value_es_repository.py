import asyncio

from elasticsearch import AsyncElasticsearch

from app.client.es_client_manager import es_client_manager
from app.core.base_log import logger
from app.models.es.value_info_es import ValueInfoES
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

    async def ensure_index(self, delete_flag=True):
        exists = await self.es_client.indices.exists(index=self.es_index_name)
        # 存在则先删除
        if exists and delete_flag:
            logger.debug("[ElasticSearch]索引[data_advisor_v1]已存在，删除重新创建...")
            await self.es_client.indices.delete(index=self.es_index_name)

        # 创建索引，传入 mapping
        await self.es_client.indices.create(
            index=self.es_index_name,
            mappings=self.es_index_mapping  # 传入你的字段映射
        )

    async def batch_index(self, docs: list[ValueInfoES], batch_size: int = 64):
        if not docs:
            return

        def generate_actions():
            for doc in docs:
                yield {
                    "_op_type": "index",  # 存在则更新，不存在则创建
                    "_index": self.es_index_name,
                    "_id": doc["id"],  # 用 id 字段作为 ES 文档 ID（TypedDict 用 doc["id"]，dataclass 用 doc.id）
                    "_source": doc  # 直接传入你的 ValueInfoES 对象
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
            results.append(source)

        return results


if __name__ == '__main__':
    async def test():
        es_client_manager.init()
        es_client = es_client_manager.client
        full_text_repository = ValueESRepository(es_client)
        await full_text_repository.ensure_index()
        query = "统计一下手机产品的销量"
        print(await full_text_repository.query(query=query))
        await es_client_manager.close()


    asyncio.run(test())
