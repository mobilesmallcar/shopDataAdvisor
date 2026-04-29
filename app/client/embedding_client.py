from pathlib import Path

from langchain_huggingface import HuggingFaceEndpointEmbeddings, HuggingFaceEmbeddings

from app.core import logger
from app.config.app_config import EmbeddingConfig, app_config


class EmbeddingClientManager:
    def __init__(self, config: EmbeddingConfig):
        self.config = config
        self.client: HuggingFaceEndpointEmbeddings | HuggingFaceEmbeddings | None = None

    def _get_model_path(self):
        model_name = self.config.model
        # 优先使用本地目录: docker/embedding/<model_name>
        local_path = Path(__file__).parents[2] / "docker" / "embedding" / model_name.replace("/", "_")
        if local_path.exists():
            logger.info(f"[词嵌入]使用本地模型:{local_path}")
            return str(local_path)
        # 回退到 HuggingFace Hub 模型名
        logger.info(f"[词嵌入]本地模型不存在,从 HuggingFace 加载:{model_name}")
        return model_name

    def init(self):
        self.client = HuggingFaceEmbeddings(
            model_name=self._get_model_path(),
            model_kwargs={
                "device": "cpu",
            },
            encode_kwargs={
                "normalize_embeddings": True,  # bge 系列需要归一化
            },
        )


embedding_client_manager = EmbeddingClientManager(app_config.embedding)

if __name__ == '__main__':
    client = EmbeddingClientManager(app_config.embedding)
    client.init()
    query = client.client.embed_query("hello world")
    print(f"向量维度: {len(query)}")
    print(query[:5])
