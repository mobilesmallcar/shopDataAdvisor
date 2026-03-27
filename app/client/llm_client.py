import asyncio
from typing import Optional

from langchain_openai import ChatOpenAI
from langchain_core.utils import convert_to_secret_str
from langchain_core.language_models import BaseChatModel

from app.config.app_config import app_config

# 全局 LLM 单例
_llm: Optional[BaseChatModel] = None


def _get_llm() -> BaseChatModel:
    """（单例模式）"""
    global _llm

    if _llm is None:
        config = app_config.llm

        _llm = ChatOpenAI(
            model=config.model_name,
            api_key=convert_to_secret_str(config.api_key),
            base_url=config.api_base,
            temperature=0.0,
            max_retries=2
        )

    return _llm


# 初始化
llm_client = _get_llm()

if __name__ == "__main__":
    async def test():
        response = await llm_client.ainvoke("中国的首都是哪里？")
        print(response)
        print(response.content)


    asyncio.run(test())
