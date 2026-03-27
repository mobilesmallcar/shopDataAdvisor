import functools
from typing import Callable, Any

from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.llm import llm_client
from app.agent.state import DataAgentState
from app.prompt.prompt_loader import load_prompt


def llm_invoke(
        prompt_name: str,
        param_builder: Callable[[DataAgentState], dict[str, Any]],
        enable_text: bool = False,
):
    """
    调用大模型
    Args:
        prompt_name: 提示词文件
        param_builder: 需要构建的大模型执行字典
        enable_text: 默认关闭,否则为Json

    Returns:

    """

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(state: DataAgentState, runtime: Runtime[DataAgentContext], *args, **kwargs) -> str:
            # 1. 构建参数
            invoke_params = param_builder(state)
            # 2. 构建提示词
            prompt = PromptTemplate(
                template=load_prompt(prompt_name),
                input_variables=list(invoke_params.keys())
            )
            # 3. 构建链
            if enable_text:
                chain = prompt | llm_client | StrOutputParser()
            else:
                chain = prompt | llm_client | JsonOutputParser()

            # 4. 调用大模型
            result = await chain.ainvoke(invoke_params)

            # 5. 返回
            return await func(state, runtime, result, *args, **kwargs)

        return wrapper

    return decorator
