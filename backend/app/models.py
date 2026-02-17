from typing import List, Optional

from pydantic import BaseModel


class IndexResponse(BaseModel):
    filename: str
    num_chunks: int
    status: str = "success"


class ChatRequest(BaseModel):
    query: str
    thread_id: Optional[str] = None


class Source(BaseModel):
    text: str
    metadata: dict


class ChatResponse(BaseModel):
    answer: str
    sources: List[Source]
    thread_id: str


class ThreadResponse(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str


class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    sources: list
    created_at: str
