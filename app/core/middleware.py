# app/core/middleware.py
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.context import request_id_ctx_var


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. 尝试从请求头获取 X-Request-ID，没有就自动生成
        request_id = request.headers.get("X-Request-ID", str("Mobile_Car"))

        # 2.1 存入上下文（全项目任意地方可用）
        request_id_ctx_var.set(request_id)

        # 2.2 存入 request.state（路由/依赖可用）
        request.state.request_id = request_id

        # 3. 处理请求
        response: Response = await call_next(request)

        # 4. 把 request_id 写回响应头
        response.headers["X-Request-ID"] = request_id
        return response
