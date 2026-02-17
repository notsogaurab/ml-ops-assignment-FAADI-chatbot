from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import chat, index, threads
from .services import database, embedding, llm, vectorstore


@asynccontextmanager
async def lifespan(app):
    _ = embedding.embedding_service
    _ = llm.llm_service
    vectorstore.vector_store.ensure_collection()
    await database.init_db()
    yield


app = FastAPI(title="RAG Backend", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(index.router)
app.include_router(chat.router)
app.include_router(threads.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
