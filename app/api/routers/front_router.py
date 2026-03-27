from fastapi import APIRouter
from fastapi.responses import FileResponse
import os

frontend_router = APIRouter(tags=["前端"])

# 获取前端文件路径
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "../../front")


@frontend_router.get("/")
@frontend_router.get("/data_view")
@frontend_router.get("/index.html")
async def chat_page():
    """返回聊天页面"""
    html_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    return {"error": "Frontend file not found", "path": html_path}


@frontend_router.get("/chat")
async def chat_page():
    """返回聊天页面"""
    html_path = os.path.join(FRONTEND_DIR, "index_chat.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    return {"error": "Frontend file not found", "path": html_path}
