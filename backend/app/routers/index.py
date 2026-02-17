from fastapi import APIRouter, File, HTTPException, UploadFile

from ..models import IndexResponse
from ..services import document, embedding, vectorstore

router = APIRouter()


@router.post("/index", response_model=IndexResponse)
async def index_document(file: UploadFile = File(...)):
    try:
        vectorstore.vector_store.ensure_collection()

        if vectorstore.vector_store.has_filename(file.filename):
            return IndexResponse(filename=file.filename, num_chunks=0, status="skipped")

        content = document.parse_file(file)

        chunks = document.chunk_text(content)

        if not chunks:
            raise HTTPException(status_code=400, detail="No text extracted from file")

        embeddings = embedding.embedding_service.encode(chunks)

        metadata = {"filename": file.filename}
        vectorstore.vector_store.upsert(chunks, embeddings, metadata)

        return IndexResponse(
            filename=file.filename, num_chunks=len(chunks), status="success"
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/index")
async def delete_index():
    try:
        vectorstore.vector_store.delete_collection()
        vectorstore.vector_store.ensure_collection()
        return {"status": "deleted", "message": "Index cleared and recreated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
