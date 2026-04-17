from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Settings:
    dataset_storage_folder: Path
    keywords_file: Path
    dataset_file: Path
    wiki_results_per_keyword: int
    wiki_request_timeout: int
    chunk_size: int
    chunk_overlap: int
    vector_db_collection: str
    vector_db_path: Path
    embedding_model: str
    chat_model_name: str
    chat_model_provider: str
    chat_model_temperature: float
    retrieval_top_k: int
    chat_history_limit: int


def _resolve_path(value: str) -> Path:
    candidate = Path(value)
    if candidate.is_absolute():
        return candidate
    return PROJECT_ROOT / candidate


def load_settings() -> Settings:
    load_dotenv(PROJECT_ROOT / ".env", override=False)

    dataset_storage_folder = _resolve_path(
        os.getenv("DATASET_STORAGE_FOLDER", "dataset")
    )
    keywords_file = _resolve_path(os.getenv("KEYWORDS_FILE", "keywords.xlsx"))
    vector_db_path = _resolve_path(os.getenv("VECTOR_DB_PATH", "chroma_db"))

    return Settings(
        dataset_storage_folder=dataset_storage_folder,
        keywords_file=keywords_file,
        dataset_file=dataset_storage_folder / "data.txt",
        wiki_results_per_keyword=int(os.getenv("WIKI_RESULTS_PER_KEYWORD", "5")),
        wiki_request_timeout=int(os.getenv("WIKI_REQUEST_TIMEOUT", "20")),
        chunk_size=int(os.getenv("CHUNK_SIZE", "1000")),
        chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "200")),
        vector_db_collection=os.getenv("VECTOR_DB_COLLECTION", "wiki_articles"),
        vector_db_path=vector_db_path,
        embedding_model=os.getenv("EMBEDDING_MODEL", "nomic-embed-text"),
        chat_model_name=os.getenv("CHAT_MODEL_NAME", "llama3.2"),
        chat_model_provider=os.getenv("CHAT_MODEL_PROVIDER", "ollama"),
        chat_model_temperature=float(os.getenv("CHAT_MODEL_TEMPERATURE", "0")),
        retrieval_top_k=int(os.getenv("RETRIEVAL_TOP_K", "3")),
        chat_history_limit=int(os.getenv("CHAT_HISTORY_LIMIT", "6")),
    )


def ensure_runtime_directories(settings: Settings) -> None:
    settings.dataset_storage_folder.mkdir(parents=True, exist_ok=True)
    settings.vector_db_path.parent.mkdir(parents=True, exist_ok=True)
