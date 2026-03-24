from langchain_huggingface import HuggingFaceEndpointEmbeddings, HuggingFaceEmbeddings

from app.config.app_config import EmbeddingConfig, app_config
from app.core.base_log import logger


class EmbeddingClientManager:
    def __init__(self, config: EmbeddingConfig):
        self.config = config
        self.client: HuggingFaceEndpointEmbeddings | HuggingFaceEmbeddings | None = None

    def _get_url(self):
        addr = f"http://{self.config.host}:{self.config.port}"
        addr = "BAAI/bge-large-zh-v1.5"
        addr = r"D:\shangguigu\github\A-Crucial-project\shopDataAdvisor\docker\embedding\bge-large-zh-v1.5"
        logger.debug(f"[词嵌入]初始化地址:{addr}")
        return addr

    def init(self):
        # self.client = HuggingFaceEndpointEmbeddings(model=self._get_url())
        self.client = HuggingFaceEmbeddings(model_name=self._get_url())


embedding_client_manager = EmbeddingClientManager(app_config.embedding)

if __name__ == '__main__':
    client = EmbeddingClientManager(app_config.embedding)
    client.init()
    query = client.client.embed_query("hello world")
    print(len(query))
    print(query)
