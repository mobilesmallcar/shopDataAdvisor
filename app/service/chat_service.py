from langgraph.graph.state import CompiledStateGraph

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.schemas.meta_client_manager_schemas import MetaClientManger


class ChatService:
    def __init__(self, graph: CompiledStateGraph, client_manager: MetaClientManger):
        self.graph = graph
        self.client_manager = client_manager

    async def stream_chat(self, query: str):
        # 1. 构建工作流和上下文
        state = DataAgentState(query=query)
        context = DataAgentContext(client_manager=self.client_manager)
        # 2. 流式执行
        async for chunk in self.graph.astream(input=state, context=context, stream_mode="custom"):
            yield chunk
