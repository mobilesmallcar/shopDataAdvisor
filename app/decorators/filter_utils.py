import functools
from typing import Callable, TypeVar
from langgraph.runtime import Runtime

from app.core import logger
from app.agent.context import DataAgentContext
from app.agent.state import TableInfoState, MetricInfoState, DataAgentState

filter_T = TypeVar("filter_T", bound=TableInfoState | MetricInfoState)  # 泛型：TableInfoState / MetricInfoState


def filter_list(get_item_list: Callable[[DataAgentState], list[filter_T]]):
    """
    列表过滤装饰器：根据名称过滤实体列表
    Args:
        get_item_list:

    Returns:

    """

    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(state, runtime, llm_result: list[str], *args, **kwargs):
            # 1. 获取:原始列表:值
            item_list = get_item_list(state)
            original_names = [item.name for item in item_list]

            # 2. 过滤:移除:被排除的值
            for item in item_list[:]:
                if item.name not in llm_result:
                    item_list.remove(item)
            # 传给原函数
            return await func(
                state, runtime,
                original_names, llm_result, item_list,
                *args, **kwargs
            )

        return wrapper

    return decorator


def log_filter(log_level: str = 'DEBUG', enabled: bool = True, print_log: str = ""):
    """
    打印过滤日志
    Args:
        log_level:
        enabled:
        print_log:

    Returns:

    """

    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(
                state: DataAgentState,
                runtime: Runtime[DataAgentContext],
                original_names: list[str],
                llm_result: list[str],
                final_rsult: list[filter_T],
                *args,
                **kwargs
        ):
            if not enabled:
                return await func(
                    state, runtime, final_rsult, *args, **kwargs)

            # 日志内容
            final_names = [item.name for item in final_rsult]
            removed_names = [n for n in original_names if n not in final_names]
            # 构建日志
            log_result = [
                f"🤖 [{print_log}]大模型筛选结果[保留]:{llm_result}",
                f"✅ [{print_log}]原始数据:{original_names}",
                f"✅ [{print_log}]最后保留的结果:{final_names}",
                f"❌ [{print_log}]被过滤掉的数据:{removed_names}"
            ]
            # 循环打印
            level = log_level.upper()
            for msg in log_result:
                if level == "DEBUG":
                    logger.debug(msg)
                elif level == "WARNING":
                    logger.warning(msg)
                else:
                    logger.info(msg)

            return await func(
                state, runtime, final_rsult, *args, **kwargs)

        return wrapper

    return decorator
