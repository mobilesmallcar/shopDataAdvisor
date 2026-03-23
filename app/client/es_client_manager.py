import asyncio
from elasticsearch import AsyncElasticsearch

from app.config.app_config import ESConfig, app_config
from app.core.base_log import logger


class ESClientManager:
    def __init__(self, config: ESConfig):
        self.config = config
        self.client: AsyncElasticsearch | None = None

    def _get_url(self):
        addr = f"http://{self.config.host}:{self.config.port}"
        logger.debug(f"[ElasticSearch]初始化地址:{addr}")
        return addr

    def init(self):
        self.client = AsyncElasticsearch(hosts=[self._get_url()], request_timeout=10000)

    async def close(self):
        await self.client.close()


es_client_manager = ESClientManager(app_config.es)

if __name__ == '__main__':
    es_client_manager.init()


    async def test():
        client = es_client_manager.client

        # 1. 创建索引
        # resp = await client.indices.create(
        #     index="my-books",
        #     mappings={
        #         "dynamic": False,
        #         "properties": {
        #             "name": {
        #                 "type": "text"
        #             },
        #             "author": {
        #                 "type": "text"
        #             },
        #             "release_date": {
        #                 "type": "date",
        #                 "format": "yyyy-MM-dd"
        #             },
        #             "page_count": {
        #                 "type": "integer"
        #             }
        #         }
        #     },
        # )
        # # 2. 批量创建数据
        # resp = await client.bulk(
        #     operations=[
        #         {
        #             "index": {
        #                 "_index": "my-books"
        #             }
        #         },
        #         {
        #             "name": "Revelation Space",
        #             "author": "Alastair Reynolds",
        #             "release_date": "2000-03-15",
        #             "page_count": 585
        #         },
        #         {
        #             "index": {
        #                 "_index": "my-books"
        #             }
        #         },
        #         {
        #             "name": "1984",
        #             "author": "George Orwell",
        #             "release_date": "1985-06-01",
        #             "page_count": 328
        #         },
        #         {
        #             "index": {
        #                 "_index": "my-books"
        #             }
        #         },
        #         {
        #             "name": "Fahrenheit 451",
        #             "author": "Ray Bradbury",
        #             "release_date": "1953-10-15",
        #             "page_count": 227
        #         },
        #         {
        #             "index": {
        #                 "_index": "my-books"
        #             }
        #         },
        #         {
        #             "name": "Brave New World",
        #             "author": "Aldous Huxley",
        #             "release_date": "1932-06-01",
        #             "page_count": 268
        #         },
        #         {
        #             "index": {
        #                 "_index": "my-books"
        #             }
        #         },
        #         {
        #             "name": "The Handmaids Tale",
        #             "author": "Margaret Atwood",
        #             "release_date": "1985-06-01",
        #             "page_count": 311
        #         }
        #     ],
        # )
        # 3. 查询数据
        resp = await client.search(
            index="my-books",
            query={
                "match": {
                    "name": "Revelation Space"
                }
            },
        )
        print(resp)
        await es_client_manager.close()


    asyncio.run(test())
