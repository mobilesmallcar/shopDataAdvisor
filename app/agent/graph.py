import asyncio

from langgraph.constants import END
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.agent.state import DataAgentState
from app.agent.context import DataAgentContext

from app.schemas.meta_client_manager_schemas import MetaClientManger
from app.service.BaseService import with_meta_clients
from app.agent.nodes import (
    add_context,
    extract_keywords,
    filter_metric_info,
    filter_table_info,
    merge_retrieved_info,
    recall_column,
    recall_metric,
    recall_value,
    correct_sql,
    execute_sql,
    generate_sql,
    validate_sql,
)


def create_main_graph() -> CompiledStateGraph:
    # 1.定义状态图
    workflow = StateGraph(state_schema=DataAgentState, context_schema=DataAgentContext)

    # 2. 定义入口节点
    nodes = {
        "extract_keywords": extract_keywords,
        "recall_column": recall_column,
        "recall_value": recall_value,
        "recall_metric": recall_metric,
        "merge_retrieved_info": merge_retrieved_info,
        "filter_table_info": filter_table_info,
        "filter_metric_info": filter_metric_info,
        "add_context": add_context,
        "generate_sql": generate_sql,
        "validate_sql": validate_sql,
        "correct_sql": correct_sql,
        "execute_sql": execute_sql,
    }
    # 3. 添加节点
    for key, value in nodes.items():
        workflow.add_node(key, value)

    # 4. 设置入口点
    workflow.set_entry_point("extract_keywords")

    # 5. 召回指标节点
    # a) 查询指标
    workflow.add_edge("extract_keywords", "recall_value")
    workflow.add_edge("extract_keywords", "recall_column")
    workflow.add_edge("extract_keywords", "recall_metric")
    # a) 合并指标
    workflow.add_edge("recall_value", "merge_retrieved_info")
    workflow.add_edge("recall_column", "merge_retrieved_info")
    workflow.add_edge("recall_metric", "merge_retrieved_info")

    # 6. 过滤指标和表信息
    workflow.add_edge("merge_retrieved_info", "filter_table_info")
    workflow.add_edge("merge_retrieved_info", "filter_metric_info")
    workflow.add_edge("filter_table_info", "add_context")
    workflow.add_edge("filter_metric_info", "add_context")

    # 7. 生成SQL
    workflow.add_edge("add_context", "generate_sql")
    workflow.add_edge("generate_sql", "validate_sql")

    # 8. 添加条件边
    workflow.add_conditional_edges(
        "validate_sql",
        lambda state: state.error is None,
        {
            True: 'execute_sql',
            False: 'correct_sql'
        }
    )
    workflow.add_edge("correct_sql", "execute_sql")
    workflow.add_edge("execute_sql", END)
    # 9. 返回可运行的状态
    return workflow.compile()


# 创建全局图实例
graph_app = create_main_graph()


@with_meta_clients
async def main(client_manager: MetaClientManger):
    # 1. 定义业务
    query_state = DataAgentState(query="统计华北地区的销售总额")

    # 2. 初始化客户端
    context = DataAgentContext(client_manager=client_manager)

    # 3. 流式执行
    async for chunk in graph_app.astream(input=query_state, context=context, stream_mode="custom"):
        print(chunk)


# 测试
if __name__ == "__main__":
    asyncio.run(main(request_id="xsy"))

    # print(graph_app.get_graph().draw_mermaid())
