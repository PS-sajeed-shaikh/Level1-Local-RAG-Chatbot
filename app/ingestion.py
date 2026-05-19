from __future__ import annotations

import shutil
from uuid import uuid4

from langchain_core.documents import Document

from app.config import ensure_runtime_directories, load_settings
from app.rag import (
    build_embeddings,
    build_text_splitter,
    build_vector_store,
    load_jsonl_records,
)


def records_to_documents(records: list[dict]) -> list[Document]:
    documents: list[Document] = []
    for record in records:
        raw_text = (record.get("raw_text") or "").strip()
        if not raw_text:
            continue

        documents.append(
            Document(
                page_content=raw_text,
                metadata={
                    "source": record["url"],
                    "title": record["title"],
                },
            )
        )
    return documents


def main() -> None:
    settings = load_settings()
    ensure_runtime_directories(settings)

    if not settings.dataset_file.exists():
        raise FileNotFoundError(
            f"Dataset file not found at {settings.dataset_file}. Run `python -m app.scraper` first."
        )

    records = load_jsonl_records(settings.dataset_file)
    source_documents = records_to_documents(records)
    splitter = build_text_splitter(settings)
    chunked_documents = splitter.split_documents(source_documents)

    embeddings = build_embeddings(settings)
    if settings.vector_db_path.exists():
        shutil.rmtree(settings.vector_db_path)

    vector_store = build_vector_store(settings, embeddings)

    ids = [str(uuid4()) for _ in chunked_documents]
    if chunked_documents:
        vector_store.add_documents(chunked_documents, ids=ids)

    print(
        f"Ingested {len(source_documents)} documents into {len(chunked_documents)} chunks "
        f"at {settings.vector_db_path}"
    )


if __name__ == "__main__":
    main()
