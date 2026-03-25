from app.client.embedding_client import embedding_client_manager
from app.client.qdrant_client_manager import qdrant_client_manager
from app.models.qdrant.column_info_qdrant import ColumnInfoQdrant
from app.repositories.qdrant.base_qdrant_repository import BaseQdrantRepository


class ColumnQdrantRepository(BaseQdrantRepository[ColumnInfoQdrant]):
    collection_name = "data_advisor_column"

    @property
    def model(self):
        return ColumnInfoQdrant


if __name__ == '__main__':
    import asyncio
    from app.schemas.meta_client_manager_schemas import MetaClientManger
    from app.service.BaseService import with_meta_clients


    @with_meta_clients
    async def main(client_manager: MetaClientManger):
        column_infos = ['销售总额', '统计', '统计华北地区的销售总额', '华北地区']
        for info in column_infos:
            query = await client_manager.embedding_client.aembed_query(info)
            result = await client_manager.column_qdrant_repository.search(
                vector=query,
                score_threshold=0.6,
                limit=10,
            )
            print(result)


    asyncio.run(main())
