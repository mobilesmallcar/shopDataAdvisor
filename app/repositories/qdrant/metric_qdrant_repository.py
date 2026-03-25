from app.models.qdrant.metric_info_qdrant import MetricInfoQdrant
from app.repositories.qdrant.base_qdrant_repository import BaseQdrantRepository


class MetricQdrantRepository(BaseQdrantRepository[MetricInfoQdrant]):
    collection_name = "data_advisor_metic"

    @property
    def model(self):
        return MetricInfoQdrant
