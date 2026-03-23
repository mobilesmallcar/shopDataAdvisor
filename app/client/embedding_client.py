from langchain_huggingface import HuggingFaceEndpointEmbeddings

from app.config.app_config import EmbeddingConfig, app_config
from app.core.base_log import logger


class EmbeddingClientManager:
    def __init__(self, config: EmbeddingConfig):
        self.config = config
        self.client: HuggingFaceEndpointEmbeddings | None = None

    def _get_url(self):
        addr = f"http://{self.config.host}:{self.config.port}"
        logger.debug(f"[词嵌入]初始化地址:{addr}")
        return addr

    def init(self):
        self.client = HuggingFaceEndpointEmbeddings(model=self._get_url())


embedding_client_manager = EmbeddingClientManager(app_config.embedding)

if __name__ == '__main__':
    client = EmbeddingClientManager(app_config.embedding)
    client.init()
    query = client.client.embed_query("hello world")
    print(len(query))
    print(query)
