import asyncio
from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import Distance, VectorParams

from app.core.base_log import logger
from app.config.app_config import QdrantConfig, app_config


class QdrantClientManager:
    def __init__(self, config: QdrantConfig):
        self.config: QdrantConfig = config
        self.client: AsyncQdrantClient | None = None

    def _get_url(self):
        addr = f"http://{self.config.host}:{self.config.port}"
        logger.debug(f"[Qdrant]初始化地址:{addr}")
        return addr

    def init(self):
        self.client = AsyncQdrantClient(url=self._get_url())

    async def close(self):
        await self.client.close()


qdrant_client_manager = QdrantClientManager(app_config.qdrant)

if __name__ == '__main__':
    qdrant_client_manager.init()


    async def test():
        client = qdrant_client_manager.client
        if not await client.collection_exists("my_collection"):
            await client.create_collection(
                collection_name="my_collection",
                vectors_config=VectorParams(size=4, distance=Distance.DOT),
            )

        # await client.upsert(
        #     collection_name="my_collection",
        #     wait=True,
        #     points=[
        #         PointStruct(id=1, vector=[0.05, 0.61, 0.76, 0.74], payload={"city": "Berlin"}),
        #         PointStruct(id=2, vector=[0.19, 0.81, 0.75, 0.11], payload={"city": "London"}),
        #         PointStruct(id=3, vector=[0.36, 0.55, 0.47, 0.94], payload={"city": "Moscow"}),
        #         PointStruct(id=4, vector=[0.18, 0.01, 0.85, 0.80], payload={"city": "New York"}),
        #         PointStruct(id=5, vector=[0.24, 0.18, 0.22, 0.44], payload={"city": "Beijing"}),
        #         PointStruct(id=6, vector=[0.35, 0.08, 0.11, 0.44], payload={"city": "Mumbai"}),
        #     ]
        # )
        search_result = await client.query_points(
            collection_name="my_collection",
            query=[0.18, 0.81, 0.75, 0.12],
            limit=1
        )
        print(search_result)


    asyncio.run(test())
