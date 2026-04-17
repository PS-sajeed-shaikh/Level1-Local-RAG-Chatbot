from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from langchain.chat_models import init_chat_model
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import Settings


def build_embeddings(settings: Settings) -> OllamaEmbeddings:
    return OllamaEmbeddings(model=settings.embedding_model)


def build_vector_store(settings: Settings, embeddings: OllamaEmbeddings) -> Chroma:
    return Chroma(
        collection_name=settings.vector_db_collection,
        embedding_function=embeddings,
        persist_directory=str(settings.vector_db_path),
    )


def build_text_splitter(settings: Settings) -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        length_function=len,
        is_separator_regex=False,
    )


def build_chat_model(settings: Settings):
    return init_chat_model(
        model=settings.chat_model_name,
        model_provider=settings.chat_model_provider,
        temperature=settings.chat_model_temperature,
    )


def load_jsonl_records(path: Path) -> list[dict]:
    records: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records


def unique_sources(documents: Iterable) -> list[str]:
    seen: set[str] = set()
    sources: list[str] = []

    for document in documents:
        source = document.metadata.get("source")
        if source and source not in seen:
            seen.add(source)
            sources.append(source)

    return sources
