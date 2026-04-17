from __future__ import annotations

import sys
from dataclasses import dataclass

from app.config import load_settings
from app.rag import build_chat_model, build_embeddings, build_vector_store


@dataclass(frozen=True)
class CheckResult:
    name: str
    ok: bool
    detail: str


def run_check(name: str, callback) -> CheckResult:
    try:
        detail = callback()
        return CheckResult(name=name, ok=True, detail=detail)
    except Exception as exc:
        return CheckResult(name=name, ok=False, detail=str(exc))


def ensure_dataset_present(settings) -> str:
    if not settings.dataset_file.exists() or settings.dataset_file.stat().st_size == 0:
        raise FileNotFoundError(f"Missing or empty dataset file at {settings.dataset_file}")
    return f"Dataset file present at {settings.dataset_file}"


def ensure_vector_store_ready(settings) -> str:
    if not settings.vector_db_path.exists():
        raise FileNotFoundError(
            f"Vector database path does not exist at {settings.vector_db_path}"
        )

    vector_store = build_vector_store(settings, build_embeddings(settings))
    count = vector_store._collection.count()
    if count == 0:
        raise RuntimeError(
            f"Collection '{settings.vector_db_collection}' exists but contains no chunks"
        )

    return f"Connected to collection '{settings.vector_db_collection}' with {count} chunks"


def main() -> int:
    settings = load_settings()

    results = [
        run_check(
            "configuration",
            lambda: (
                "Settings loaded successfully "
                f"(dataset={settings.dataset_file}, vector_db={settings.vector_db_path})"
            ),
        ),
        run_check(
            "dataset availability",
            lambda: ensure_dataset_present(settings),
        ),
        run_check(
            "vector database connectivity",
            lambda: ensure_vector_store_ready(settings),
        ),
        run_check(
            "embedding model readiness",
            lambda: (
                f"Embedding vector length: {len(build_embeddings(settings).embed_query('health check'))}"
            ),
        ),
        run_check(
            "LLM availability",
            lambda: (
                f"LLM response: {str(build_chat_model(settings).invoke('Reply with OK only.').content).strip()}"
            ),
        ),
    ]

    for result in results:
        status = "OK" if result.ok else "FAIL"
        print(f"[{status}] {result.name}: {result.detail}")

    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    sys.exit(main())
