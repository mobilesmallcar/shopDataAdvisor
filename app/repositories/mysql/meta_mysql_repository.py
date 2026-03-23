from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mysql.column_info_mysql import ColumnInfoMySQL
from app.models.mysql.table_info_mysql import TableInfoMySQL


class MetaMysqlRepository:
    def __init__(self, meta_session: AsyncSession):
        self.meta_session = meta_session

    async def save_table_infos(self, table_infos: list[TableInfoMySQL]):
        self.meta_session.add_all(table_infos)

    async def save_column_infos(self, column_infos: list[ColumnInfoMySQL]):
        self.meta_session.add_all(column_infos)
