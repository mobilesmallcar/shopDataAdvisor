from typing import Sequence

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import TableInfoMySQL, ColumnInfoMySQL, MetricInfoMySQL, ColumnMetricMySQL


class MetaMysqlRepository:
    def __init__(self, meta_session: AsyncSession):
        self.meta_session = meta_session

    async def save_table_infos(self, table_infos: list[TableInfoMySQL]):
        self.meta_session.add_all(table_infos)

    async def save_column_infos(self, column_infos: list[ColumnInfoMySQL]):
        self.meta_session.add_all(column_infos)

    async def save_metric_infos(self, table_infos: list[MetricInfoMySQL]):
        self.meta_session.add_all(table_infos)

    async def save_column_metic_infos(self, column_infos: list[ColumnMetricMySQL]):
        self.meta_session.add_all(column_infos)

    async def get_column_by_id(self, column_id) -> ColumnInfoMySQL | None:
        return await self.meta_session.get(ColumnInfoMySQL, column_id)

    async def get_columns_by_ids(self, column_ids) -> Sequence[ColumnInfoMySQL]:
        # 构建语句:查询所有列信息
        stmt = select(ColumnInfoMySQL).where(ColumnInfoMySQL.id.in_(column_ids))

        result = await self.meta_session.execute(stmt)
        return result.scalars().all()

    async def get_table_by_id(self, column_id) -> ColumnInfoMySQL | None:
        return await self.meta_session.get(ColumnInfoMySQL, column_id)

    async def get_table_by_ids(self, table_ids: list[str]) -> Sequence[TableInfoMySQL]:
        # 构建语句:查询所有table信息
        stmt = select(TableInfoMySQL).where(TableInfoMySQL.id.in_(table_ids))

        result = await self.meta_session.execute(stmt)
        return result.scalars().all()

    async def get_key_columns_by_table_ids(self, table_id: str) -> Sequence[ColumnInfoMySQL]:
        stmt = select(ColumnInfoMySQL).where(
            ColumnInfoMySQL.table_id == table_id,
            ColumnInfoMySQL.role.in_(['primary_key', 'foreign_key'])
        )
        # 执行返回
        result = await self.meta_session.execute(stmt)
        return result.scalars().all()
