from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState, TableInfoState

# 导入装饰器
from app.decorators import llm_invoke, filter_list, log_filter


def get_table_list(state: DataAgentState) -> list[TableInfoState]:
    return state.table_infos


@llm_invoke(
    prompt_name="filter_table_info",
    param_builder=lambda state: {
        "query": state.query,
        "table_infos": get_table_list(state)
    }
)
@filter_list(get_item_list=get_table_list)
@log_filter(log_level="debug", enabled=True, print_log="过滤表格信息")
async def filter_table_info(
        state: DataAgentState,
        runtime: Runtime[DataAgentContext],
        final_rsult: list[TableInfoState]
):
    writer = runtime.stream_writer
    writer("过滤指标信息")
    return {"table_infos": final_rsult}

# async def filter_table_info(
#         state: DataAgentState,
# ):
#
#     from app.agent.llm import llm_client
#     from app.core import logger
#     from app.prompt.prompt_loader import load_prompt
#     from langchain_core.output_parsers import JsonOutputParser
#     from langchain_core.prompts import PromptTemplate
#     writer = runtime.stream_writer
#     writer("过滤表格信息")
#     table_infos: list[TableInfoState] = state.table_infos
#     query = state.query
#
#     try:
#         logger.debug(f"📥 原始待过滤指标列表：")
#         for idx, m in enumerate(table_infos):
#             logger.debug(f"  {idx + 1}. {m.name} -> {m.description}")
#
#         # 执行 LLM 过滤
#         prompt = PromptTemplate(
#             template=load_prompt("filter_table_info"),
#             input_variables=['query', 'table_infos']
#         )
#         output_parser = JsonOutputParser()
#         chain = prompt | llm_client | output_parser
#
#         result = await chain.ainvoke({
#             "query": query,
#             "table_infos": table_infos
#         })
#
#         # 🔍 DEBUG 2：打印【大模型返回的结果】
#         logger.debug(f"🤖 大模型筛选结果（需要保留的指标）：{result}")
#
#         # 开始过滤
#         original_names = [m.name for m in table_infos]
#         for metric_info in table_infos[:]:
#             if metric_info.name not in result:
#                 table_infos.remove(metric_info)
#
#         # 🔍 INFO 3：打印【最终保留的指标】
#         final_names = [m.name for m in table_infos]
#         removed_names = [name for name in original_names if name not in final_names]
#
#         logger.info(f"✅ 最终保留指标：{final_names} ❌ 被过滤掉指标：{removed_names} ")
#
#         return {"table_infos": table_infos}
#
#     except Exception as e:
#         logger.error(f"❌ 过滤指标信息失败: {str(e)}")
#         # 出错时也打印关键信息，方便排查
#         logger.error(f"❌ 失败时原始指标: {[m.name for m in table_infos]}")
#         raise
