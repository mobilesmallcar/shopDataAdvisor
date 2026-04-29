from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers.chat_router import chat_router
from app.api.routers.front_router import frontend_router
from app.core.lifesapn import lifespan
from app.core.middleware import RequestIDMiddleware


def create_app() -> FastAPI:
    # 1. 实例化FastAPI
    app = FastAPI(
        lifespan=lifespan,  # 生命周期管理,管理数据库
        title="Query Service",
        description="知识库查询服务"
    )

    # 2.1 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], allow_credentials=True,
        allow_methods=["*"], allow_headers=["*"],
    )
    # 2.2 添加request_id中间件
    app.add_middleware(RequestIDMiddleware)

    # 3. 添加路由
    app.include_router(
        chat_router,
        prefix="/api",  # 统一前缀
        tags=["用户模块"],  # Swagger 分组
    )
    app.include_router(frontend_router)
    # 4. 返回实例
    return app


app: FastAPI = create_app()
