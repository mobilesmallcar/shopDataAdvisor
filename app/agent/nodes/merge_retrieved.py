from pprint import pformat
from typing import Sequence

from langgraph.runtime import Runtime

from app.core import logger
from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState, ColumnInfoState, TableInfoState, MetricInfoState
from app.decorators import writer_node

# 导入仓库
from app.repositories import MetaMysqlRepository
# 导入模型
from app.models import ColumnInfoMySQL, TableInfoMySQL, ColumnInfoQdrant, MetricInfoQdrant, ValueInfoES


@writer_node("合并召回信息")
async def merge_retrieved_info(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    # writer = runtime.stream_writer
    # writer({"process": "合并召回信息"})

    # 获取需要合并的对象 和 对应的仓库
    retrieved_columns: list[ColumnInfoQdrant] = state.retrieved_columns
    retrieved_metrics: list[MetricInfoQdrant] = state.retrieved_metrics
    retrieved_values: list[ValueInfoES] = state.retrieved_values

    meta_repository: MetaMysqlRepository = runtime.context.client_manager.meta_repository

    logger.debug(f"需要合并的对象:\n{pformat(retrieved_values, indent=2)}")
    logger.debug(f"需要合并的对象:\n{pformat(retrieved_metrics, indent=2)}")
    logger.debug(f"需要合并的对象:\n{pformat(retrieved_columns, indent=2)}")

    map_column_id2obj: dict[str, ColumnInfoQdrant] = {val.id: val for val in retrieved_columns}
    # 1. 把值信息和指标信息合并进列信息
    # a) 合并值信息
    metric_column_ids: list[str] = [column_id
                                    for val in retrieved_metrics
                                    for column_id in val.relevant_columns or []]
    column_infos: Sequence[ColumnInfoMySQL] \
        = await meta_repository.get_columns_by_ids(
        list(set(
            list(map_column_id2obj.keys()) + metric_column_ids
        ))
    )
    map_column_id2sqlObj = {val.id: val for val in column_infos}
    for es_info in retrieved_values:
        # 1. 获取:列名
        column_id = es_info.column_id
        # 2. 获取:值
        value = es_info.value
        # 3. 列:已召回->判断值是否需要插入
        if column_id in map_column_id2obj:
            # 3.1 值:不存在:则加入
            if value not in map_column_id2obj[column_id].examples:
                map_column_id2obj[column_id].examples.append(value)
        # 4. 列:未召回->判断列和值是否都需要插入
        else:
            # 4.1 查询:列信息
            column_info: ColumnInfoMySQL = map_column_id2sqlObj.get(column_id)
            # 4.2 值:不存在列的示例:插入
            if value not in column_info.examples:
                column_info.examples.append(value)
            # 4.3 列:转化并插入
            map_column_id2obj[column_id] = ColumnInfoQdrant.model_validate(column_info)

    # b) 合并指标信息
    for metric_info in retrieved_metrics:
        # 1. 获取:多个列名
        column_ids = metric_info.relevant_columns
        # 2. 遍历:每个列名->判断是否要插入
        for column_id in column_ids:
            # 2.1 列:不存在
            if column_id not in map_column_id2obj:
                # 2.2 列:查询
                column_info: ColumnInfoMySQL = map_column_id2sqlObj.get(column_id)
                # 2.2 列:转化并插入
                map_column_id2obj[column_id] = ColumnInfoQdrant.model_validate(column_info)

    # 2. 构建表列信息
    final_table_infos: list[TableInfoState] = []
    # a) 构建:<表名:list[列信息]>映射
    map_table_id2columns: dict[str, list[ColumnInfoQdrant]] = {}
    for column in map_column_id2obj.values():
        # 1. 获取:表名
        table_id = column.table_id
        # 2. 表名:不存在:赋值
        if table_id not in map_table_id2columns:
            map_table_id2columns[table_id] = []
        # 3. 表名:已存在:添加列信息
        map_table_id2columns[table_id].append(column)

    # b) 构建:表信息[列信息]
    table_infos: Sequence[TableInfoMySQL] = await meta_repository.get_table_by_ids(list(map_table_id2columns.keys()))
    for table_info in table_infos:
        # 1.定义:列对象 && 列ID
        column_states: list[ColumnInfoState] = []
        column_state_ids: list[str] = []

        # 2. 构建:列信息
        for column in map_table_id2columns[table_info.id]:
            # 2.1 转化:列信息
            column_state = ColumnInfoState.model_validate(column)
            # 2.2 添加:列信息
            column_states.append(column_state)
            # 2.3 构建:列ID
            column_state_ids.append(column.id)

        # 3. 构建:完整列信息:用主外键
        key_columns = await meta_repository.get_key_columns_by_table_ids(table_info.id)
        for key_column in key_columns:
            # 3.1 列:不存在
            if key_column.id not in column_state_ids:
                # 3.2 列:转化:列信息
                column_state = ColumnInfoState.model_validate(key_column)
                # 3.3 添加:列信息
                column_states.append(column_state)

        # 4. 构建表信息
        table_info_state = TableInfoState(
            name=table_info.name,
            role=table_info.role,
            description=table_info.description,
            columns=column_states
        )
        final_table_infos.append(table_info_state)

    # 3. 构建指标信息
    final_metric_infos: list[MetricInfoState] = [MetricInfoState.model_validate(metric) for metric in retrieved_metrics]

    logger.info(f"召回信息合并成功")
    return {"table_infos": final_table_infos, "metric_infos": final_metric_infos}
