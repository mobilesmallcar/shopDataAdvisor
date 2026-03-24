import asyncio

from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.agent.context import DataAgentContext
from app.agent.nodes.add_context import add_context
from app.agent.nodes.extract_keywords import extract_keywords
from app.agent.nodes.filter_metric import filter_metric_info
from app.agent.nodes.filter_table import filter_table_info
from app.agent.nodes.merge_retrieved import merge_retrieved_info
from app.agent.nodes.recall_column import recall_column
from app.agent.nodes.recall_metric import recall_metric
from app.agent.nodes.recall_value import recall_value
from app.agent.nodes.sql_correct import correct_sql
from app.agent.nodes.sql_execute import execute_sql
from app.agent.nodes.sql_generate import generate_sql
from app.agent.nodes.sql_vaildate import validate_sql
from app.agent.state import DataAgentState


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

# 测试
if __name__ == "__main__":
    async def test():

        my_test_state = DataAgentState(query="统计华北地区的销售总额")
        context = DataAgentContext()
        async for chunk in graph_app.astream(input=my_test_state, context=context, stream_mode="custom"):
            print(chunk)


    asyncio.run(test())

    print(graph_app.get_graph().draw_mermaid())
