import sys
import uuid
import os
import logging
from pathlib import Path

from loguru import logger # 必须保留

from app.config.app_config import app_config
from app.core.context import request_id_ctx_var

# ======================
# 日志格式
# ======================
log_format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<magenta>request_id - {extra[request_id]}</magenta> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)


# ======================
# 禁用第三方日志
# ======================
def disable_noise_logs():
    import jieba
    jieba.setLogLevel(60)

    os.environ["TQDM_DISABLE"] = "1"
    os.environ["TOKENIZERS_PARALLELISM"] = "false"

    logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
    logging.getLogger("huggingface").setLevel(logging.ERROR)
    logging.getLogger("transformers").setLevel(logging.ERROR)
    logging.getLogger("bert").setLevel(logging.ERROR)
    logging.getLogger("qdrant").setLevel(logging.ERROR)


# ======================
# 请求ID注入
# ======================
def inject_request_id(record):
    try:
        request_id = request_id_ctx_var.get()
    except Exception:
        request_id = uuid.uuid4()
    record["extra"]["request_id"] = request_id


# ======================
# 初始化日志
# ======================
def setup_logger():
    global logger
    logger.remove()
    logger = logger.patch(inject_request_id)

    # 控制台
    if app_config.logging.console.enable:
        logger.add(
            sink=sys.stdout,
            level=app_config.logging.console.level,
            format=log_format
        )
    # 文件
    if app_config.logging.file.enable:
        log_path = Path(app_config.logging.file.path)
        log_path.mkdir(parents=True, exist_ok=True)
        logger.add(
            sink=log_path / "app.log",
            level=app_config.logging.file.level,
            format=log_format,
            rotation=app_config.logging.file.rotation,
            retention=app_config.logging.file.retention,
            encoding="utf-8"
        )


# ======================
# 全局自动初始化
# ======================
setup_logger()
disable_noise_logs()

# ======================
# 对外导出 logger
# ======================
from loguru._logger import Logger

logger: Logger

if __name__ == '__main__':
    logger.info("hello world")
