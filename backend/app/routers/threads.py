from typing import List

from fastapi import APIRouter, HTTPException

from ..models import MessageResponse, ThreadResponse
from ..services import database

router = APIRouter()


@router.get("/threads", response_model=List[ThreadResponse])
async def list_threads():
    threads = await database.get_all_threads()
    return threads


@router.post("/threads", response_model=ThreadResponse)
async def create_thread(title: str = "New Chat"):
    thread = await database.create_thread(title)
    return thread


@router.get("/threads/{thread_id}", response_model=ThreadResponse)
async def get_thread(thread_id: str):
    thread = await database.get_thread(thread_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    return thread


@router.get("/threads/{thread_id}/messages", response_model=List[MessageResponse])
async def get_messages(thread_id: str):
    thread = await database.get_thread(thread_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    messages = await database.get_thread_messages(thread_id)
    return messages


@router.put("/threads/{thread_id}", response_model=ThreadResponse)
async def update_thread(thread_id: str, title: str):
    thread = await database.get_thread(thread_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    await database.update_thread_title(thread_id, title)
    return await database.get_thread(thread_id)


@router.delete("/threads/{thread_id}")
async def delete_thread_endpoint(thread_id: str):
    thread = await database.get_thread(thread_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    await database.delete_thread(thread_id)
    return {"status": "deleted"}
