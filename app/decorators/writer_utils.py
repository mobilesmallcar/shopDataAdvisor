from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState


def writer_node(step_name: str):
    def decorator(func):
        async def wrapper(state: DataAgentState, runtime: Runtime[DataAgentContext]):
            writer = runtime.stream_writer

            # ========== 步骤开始 ==========
            writer({
                "type": "progress",
                "step": step_name,
                "status": "running"
            })

            try:
                # 执行原函数
                result = await func(state, runtime)

                # ========== 步骤成功 ==========
                writer({
                    "type": "progress",
                    "step": step_name,
                    "status": "success"
                })

                return result

            except Exception as e:
                # ========== 步骤失败 ==========
                writer({
                    "type": "progress",
                    "step": step_name,
                    "status": "error"
                })
                raise  # 把异常继续抛出去

        return wrapper

    return decorator