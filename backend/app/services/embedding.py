import torch
from sentence_transformers import SentenceTransformer

from .. import config


class EmbeddingService:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = SentenceTransformer(
            config.settings.EMBEDDING_MODEL, device=self.device
        )

    def encode(self, texts):
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()


embedding_service = EmbeddingService()
