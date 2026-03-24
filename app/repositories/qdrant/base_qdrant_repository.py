from typing import TypeVar, Generic

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

from app.config.app_config import app_config
from app.core.base_log import logger

T = TypeVar('T')


class BaseQdrantRepository(Generic[T]):
    collection_name: str

    def __init__(self, client: AsyncQdrantClient):
        self.client = client

    async def delete_collection(self):
        await self.client.delete_collection(self.collection_name)
        logger.debug(f"[Qdrant]集合[{self.collection_name}]已删除")

    async def ensure_collection(self):
        # 1.判断结合是否存在
        exist = await self.client.collection_exists(self.collection_name)
        # 2.如若不存在,则创建集合
        if not exist:
            await self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=app_config.qdrant.embedding_size,
                    distance=Distance.COSINE
                ),
            )
            logger.debug("[Qdrant]集合[{self.collection_name}]已创建")
        else:
            logger.debug("[Qdrant]集合[{self.collection_name}]已存在,返回..")

    async def upsert(
            self,
            ids: list,
            embeddings: list[list[float]],
            payloads: list[T],
            batch_size: int = 64,
    ) -> None:
        """批量插入/更新点"""
        if not ids:
            return

        # 构造 PointStruct（支持 Pydantic 对象和 dict）
        points: list[PointStruct] = [
            PointStruct(
                id=point_id,
                vector=embedding,
                payload=(
                    payload
                    if isinstance(payload, dict)
                    else payload.model_dump(mode="json")
                ),
            )
            for point_id, embedding, payload in zip(ids, embeddings, payloads)
        ]

        # 使用 upload_points（官方强烈推荐，比手动循环 upsert 更好）
        self.client.upload_points(  # type: ignore[misc]
            collection_name=self.collection_name,
            points=points,
            batch_size=batch_size,
            # parallel=2,      # 如果数据量非常大，可以打开
        )

    async def search(
            self,
            vector: list[float],
            score_threshold: float = 0.6,
            limit: int = 10,
    ) -> list[T]:
        result = await self.client.query_points(
            collection_name=self.collection_name,
            query=vector,  # type: ignore[arg-type]
            score_threshold=score_threshold,
            limit=limit,
        )
        return [point.payload for point in result.points]
