from app.client.embedding_client import embedding_client_manager
from app.client.qdrant_client_manager import qdrant_client_manager
from app.models.qdrant.column_info_qdrant import ColumnInfoQdrant
from app.repositories.qdrant.base_qdrant_repository import BaseQdrantRepository


class ColumnQdrantRepository(BaseQdrantRepository[ColumnInfoQdrant]):
    collection_name = "data_advisor_column"


if __name__ == "__main__":
    import asyncio


    async def test():
        embedding_client_manager.init()
        embedding_client = embedding_client_manager.client

        qdrant_client_manager.init()
        column_qdrant_repository = ColumnQdrantRepository(qdrant_client_manager.client)

        await column_qdrant_repository.ensure_collection(delete_flag=True)
        query = "统计一下销售总额"
        result = await column_qdrant_repository.search(embedding_client.embed_query(query))
        print(result)


    asyncio.run(test())
