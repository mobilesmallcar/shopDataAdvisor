from dataclasses import dataclass

from app.client.mysql_client_manager import MySQLClientManager
from app.repositories.mysql.dw_mysql_repository import DWMysqlRepository
from app.repositories.mysql.meta_mysql_repository import MetaMysqlRepository


@dataclass
class MetaClientManger:
    dw_repository: DWMysqlRepository
    meta_repository: MetaMysqlRepository
