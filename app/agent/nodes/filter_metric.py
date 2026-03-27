from typing import Any

from langgraph.runtime import Runtime
from app.agent.nodes.decorator_utils.llm_utils import llm_invoke
from app.agent.nodes.decorator_utils.filter_utils import filter_list, log_filter
from app.agent.state import DataAgentState, MetricInfoState
from app.agent.context import DataAgentContext


def get_metric_list(state: DataAgentState) -> list[MetricInfoState]:
    return state.metric_infos


def build_metric_params(state: DataAgentState) -> dict[str, Any]:
    return {
        "query": state.query,
        "metric_infos": get_metric_list(state)
    }


@llm_invoke(
    prompt_name="filter_metric_info",
    param_builder=build_metric_params  # 直接传方法！
)
@filter_list(get_item_list=get_metric_list)
@log_filter(log_level="debug", enabled=True, print_log="过滤指标信息")
async def filter_metric_info(
        state: DataAgentState,
        runtime: Runtime[DataAgentContext],
        final_rsult: list[MetricInfoState]
):
    writer = runtime.stream_writer
    writer("过滤指标信息")
    return {"metric_infos": final_rsult}

# async def filter_metric_info(
#         state: DataAgentState,
#         runtime: Runtime[DataAgentContext],
# ):
#
#     from app.agent.llm import llm_client
#     from app.core.base_log import logger
#     from app.prompt.prompt_loader import load_prompt
#     from langchain_core.output_parsers import JsonOutputParser
#     from langchain_core.prompts import PromptTemplate
#     metric_infos: list[MetricInfoState] = state.metric_infos
#     query = state.query
#
#     try:
#         logger.debug(f"📥 原始待过滤指标列表：")
#         for idx, m in enumerate(metric_infos):
#             logger.debug(f"  {idx + 1}. {m.name} -> {m.description}")
#
#         # 执行 LLM 过滤
#         prompt = PromptTemplate(
#             template=load_prompt("filter_metric_info"),
#             input_variables=['query', 'metric_infos']
#         )
#         output_parser = JsonOutputParser()
#         chain = prompt | llm_client | output_parser
#
#         result = await chain.ainvoke({
#             "query": query,
#             "metric_infos": metric_infos
#         })
#
#         # 🔍 DEBUG 2：打印【大模型返回的结果】
#         logger.debug(f"🤖 大模型筛选结果（需要保留的指标）：{result}")
#
#         # 开始过滤
#         original_names = [m.name for m in metric_infos]
#         for metric_info in metric_infos[:]:
#             if metric_info.name not in result:
#                 metric_infos.remove(metric_info)
#
#         # 🔍 INFO 3：打印【最终保留的指标】
#         final_names = [m.name for m in metric_infos]
#         removed_names = [name for name in original_names if name not in final_names]
#
#         logger.info(f"✅ 最终保留指标：{final_names} ❌ 被过滤掉指标：{removed_names} ")
#
#         return {"metric_infos": metric_infos}
#
#     except Exception as e:
#         logger.error(f"❌ 过滤指标信息失败: {str(e)}")
#         # 出错时也打印关键信息，方便排查
#         logger.error(f"❌ 失败时原始指标: {[m.name for m in metric_infos]}")
#         raise
