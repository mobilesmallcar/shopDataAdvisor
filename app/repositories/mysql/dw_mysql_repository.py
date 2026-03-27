from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class DWMysqlRepository:
    # 1. 定义允许的表名白名单
    ALLOWED_TABLES = {"dim_customer", "dim_date", "dim_product", "dim_region", "fact_order"}

    def __init__(self, dw_session: AsyncSession):
        self.dw_session = dw_session

    def check_table_name(self, table_name):
        if table_name not in self.ALLOWED_TABLES:
            raise PermissionError(f"Table '{table_name}' is not allowed to be inspected.")

    async def get_column_types(self, table_name: str) -> dict[str, str]:
        """
        获取表中个字段类型
        Args:
            table_name: 表名

        Returns:
            {字段名,字段类型}
        """
        self.check_table_name(table_name)
        sql = text(f"SHOW COLUMNS FROM `{table_name}`")
        result = await self.dw_session.execute(sql)
        return {row.Field: row.Type for row in result.fetchall()}

    async def get_column_values(self, table_name: str, column_name: str, limit: int) -> list:
        """
        返回当前列下所有去重后的值
        Args:
            table_name: 表名
            column_name: 列名
            limit: 返回的限制

        Returns:
            list
        """
        self.check_table_name(table_name)
        sql = text(f"""
            SELECT 
                {column_name} as column_name 
            FROM {table_name} 
            GROUP BY {column_name} 
            LIMIT {limit}
        """)
        result = await self.dw_session.execute(sql)
        return [row.column_name for row in result.fetchall()]

    async def get_db_info(self):
        """
        获取数据仓信息
        Returns: 数据仓信息

        """
        dialect = self.dw_session.get_bind().dialect.name

        sql = text("SELECT version() as version")

        result = await self.dw_session.execute(sql)
        version = result.scalar().strip()

        return {"dialect": dialect, "version": version}

    async def validate_sql(self, sql):
        await self.dw_session.execute(text(f"EXPLAIN {sql}"))

    async def execute_sql(self, sql):
        result = await self.dw_session.execute(text(sql))
        return [dict(row) for row in result.mappings().fetchall()]
