from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    QDRANT_HOST: str = "local"  # Changed default to local for no-docker run
    QDRANT_PORT: int = 6333
    QDRANT_PATH: str = "./qdrant_storage"  # Data path for local mode
    COLLECTION_NAME: str = "documents"
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
    LLM_MODEL: str = "Qwen/Qwen2.5-0.5B-Instruct"
    CHUNK_SIZE: int = 1024
    CHUNK_OVERLAP: int = 100

    class Config:
        env_file = ".env"


settings = Settings()
