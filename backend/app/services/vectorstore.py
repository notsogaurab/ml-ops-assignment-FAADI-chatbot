import os
import uuid

from qdrant_client import QdrantClient
from qdrant_client.http import models

from .. import config


class VectorStoreService:
    def __init__(self):
        if config.settings.QDRANT_HOST == "local":
            print(f"Using local Qdrant at {config.settings.QDRANT_PATH}")
            os.makedirs(config.settings.QDRANT_PATH, exist_ok=True)
            self.client = QdrantClient(path=config.settings.QDRANT_PATH)
        else:
            self.client = QdrantClient(
                host=config.settings.QDRANT_HOST, port=config.settings.QDRANT_PORT
            )

        self.collection_name = config.settings.COLLECTION_NAME
        self.vector_size = 384

    def ensure_collection(self):
        try:
            self.client.get_collection(self.collection_name)
        except Exception:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=self.vector_size, distance=models.Distance.COSINE
                ),
            )

    def delete_collection(self):
        try:
            self.client.delete_collection(self.collection_name)
        except Exception:
            pass

    def has_filename(self, filename):
        try:
            results = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="filename",
                            match=models.MatchValue(value=filename),
                        )
                    ]
                ),
                limit=1,
            )
            return len(results[0]) > 0
        except Exception:
            return False

    def upsert(self, chunks, embeddings, metadata):
        points = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            points.append(
                models.PointStruct(
                    id=str(uuid.uuid4()),
                    vector=embedding,
                    payload={"text": chunk, **metadata},
                )
            )

        self.client.upsert(collection_name=self.collection_name, points=points)

    def search(self, query_embedding, limit=5):
        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding,
            limit=limit,
        )
        return [
            {"text": hit.payload["text"], "score": hit.score, "metadata": hit.payload}
            for hit in results.points
        ]


vector_store = VectorStoreService()
