from fastapi import APIRouter, HTTPException

from ..models import ChatRequest, ChatResponse, Source
from ..services import database, embedding, llm, vectorstore

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        thread_id = request.thread_id
        if not thread_id:
            title = request.query[:50] + ("..." if len(request.query) > 50 else "")
            thread = await database.create_thread(title)
            thread_id = thread["id"]

        await database.add_message(thread_id, "user", request.query)

        chat_history = await database.get_recent_history(thread_id, limit=10)

        query_embedding = embedding.embedding_service.encode([request.query])[0]

        vectorstore.vector_store.ensure_collection()
        search_results = vectorstore.vector_store.search(query_embedding, limit=3)

        context_parts = [res["text"] for res in search_results]

        if not context_parts:
            answer = "I don't have any documents indexed to answer this question."
        else:
            answer = llm.llm_service.generate(
                context_parts, request.query, chat_history
            )

        sources = [
            Source(text=res["text"], metadata=res["metadata"]) for res in search_results
        ]

        sources_for_db = [{"text": s.text, "metadata": s.metadata} for s in sources]
        await database.add_message(thread_id, "assistant", answer, sources_for_db)

        return ChatResponse(answer=answer, sources=sources, thread_id=thread_id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
