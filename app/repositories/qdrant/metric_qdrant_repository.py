from app.models.qdrant.metric_info_qdrant import MetricInfoQdrant
from app.repositories.qdrant.base_qdrant_repository import BaseQdrantRepository


class MetricQdrantRepository(BaseQdrantRepository[MetricInfoQdrant]):
    collection_name = "data_advisor_metic"

    @property
    def model(self):
        return MetricInfoQdrant


if __name__ == '__main__':
    import asyncio
    from app.schemas.meta_client_manager_schemas import MetaClientManger
    from app.service.BaseService import with_meta_clients


    @with_meta_clients
    async def main(client_manager: MetaClientManger):
        metric_infos = ['华北地区', '统计华北地区的销售总额', '销售总额', '统计日期', '销售金额', '销售区域', '统计']
        for info in metric_infos:
            query = await client_manager.embedding_client.aembed_query(info)
            result = await client_manager.metric_qdrant_repository.search(
                vector=query,
                score_threshold=0.6,
                limit=10,
            )
            print(result)


    asyncio.run(main())
