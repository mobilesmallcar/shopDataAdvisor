import json

from fastapi import APIRouter, Depends
from starlette.responses import StreamingResponse

from app.api.dependencies import get_chat_service

from app.schemas import QuerySchema
from app.service import ChatService

# 定义router
chat_router = APIRouter()


@chat_router.post("/query")
def data_query(query: QuerySchema, chat_service: ChatService = Depends(get_chat_service)):
    async def event_stream():
        # async for chunk in chat_service.stream_chat(query.query):
        #     yield f"data: {json.dumps(chunk, ensure_ascii=False, default=str)}\n\n"
        try:
            async for chunk in chat_service.stream_chat(query.query):
                yield f"data: {json.dumps(chunk, ensure_ascii=False, default=str)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False, default=str)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
    )
