import asyncio

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langgraph.runtime import Runtime

from app.core.base_log import logger
from app.agent.llm import llm_client
from app.agent.state import DataAgentState
from app.agent.context import DataAgentContext
from app.models.qdrant.column_info_qdrant import ColumnInfoQdrant
from app.prompt.prompt_loader import load_prompt
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository


async def recall_column(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    """

    Args:
        state: query,keyword
        runtime:

    Returns:

    """
    writer = runtime.stream_writer
    writer("召回字段")

    # 1. 获取向量仓库 和嵌入客户端
    query = state.query
    keywords = state.keywords
    column_qdrant_repository: ColumnQdrantRepository = runtime.context.client_manager.column_qdrant_repository
    embedding_client: HuggingFaceEmbeddings = runtime.context.client_manager.embedding_client

    # 2. 获取模版
    prompt = PromptTemplate(template=load_prompt("extend_keywords_for_column_recall"), input_variables=["query"])
    # 3. 构建链
    output_parser = JsonOutputParser()
    chain = prompt | llm_client | output_parser

    # 4. 获取大模型的列召回并合并
    result_content = await chain.ainvoke({"query": query})
    keywords = list(set(keywords + result_content))

    # 5. 获取向量仓库的列召回并合并
    columns_map: dict[str, ColumnInfoQdrant] = {}
    for key in keywords:
        embedding = await embedding_client.aembed_query(key)
        columns: list[ColumnInfoQdrant] = await column_qdrant_repository.search(embedding, 0.6, 5)
        for column in columns:
            if column.id not in columns_map:
                columns_map[column.id] = column
    retrieved_columns = columns_map.values()
    logger.info(f"字段信息召回成功: {columns_map.keys()}")

    return {"retrieved_columns": list(retrieved_columns)}
