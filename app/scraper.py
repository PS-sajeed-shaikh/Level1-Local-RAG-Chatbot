from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Iterable
from urllib.parse import quote

import pandas as pd
import requests

from app.config import ensure_runtime_directories, load_settings


SEARCH_ENDPOINT = "https://en.wikipedia.org/w/api.php"
SUMMARY_ENDPOINT = "https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
USER_AGENT = "Level1-Local-RAG/1.0 (Wikipedia educational scraper)"


@dataclass(frozen=True)
class ArticleSummary:
    title: str
    url: str
    raw_text: str


def load_keywords(keywords_file) -> list[str]:
    dataframe = pd.read_excel(keywords_file)
    if "Keyword" not in dataframe.columns:
        raise ValueError(
            f"Expected a 'Keyword' column in {keywords_file}, but it was not found."
        )

    keywords = [
        str(value).strip()
        for value in dataframe["Keyword"].dropna().tolist()
        if str(value).strip()
    ]

    if not keywords:
        raise ValueError(f"No keywords found in {keywords_file}.")

    return keywords


def search_wikipedia(keyword: str, limit: int, timeout: int) -> list[str]:
    response = requests.get(
        SEARCH_ENDPOINT,
        params={
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": keyword,
            "srlimit": limit,
            "utf8": 1,
        },
        headers={"User-Agent": USER_AGENT},
        timeout=timeout,
    )
    response.raise_for_status()
    payload = response.json()
    return [item["title"] for item in payload.get("query", {}).get("search", [])]


def fetch_summary(title: str, timeout: int) -> ArticleSummary | None:
    encoded_title = quote(title.replace(" ", "_"), safe="")
    response = requests.get(
        SUMMARY_ENDPOINT.format(title=encoded_title),
        headers={"User-Agent": USER_AGENT},
        timeout=timeout,
    )

    if response.status_code == 404:
        return None

    response.raise_for_status()
    payload = response.json()

    raw_text = (payload.get("extract") or "").strip()
    if not raw_text or payload.get("type") == "disambiguation":
        return None

    url = (
        payload.get("content_urls", {})
        .get("desktop", {})
        .get("page", f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}")
    )

    return ArticleSummary(
        title=payload.get("title", title),
        url=url,
        raw_text=raw_text,
    )


def collect_articles(
    keywords: Iterable[str], results_per_keyword: int, timeout: int
) -> list[ArticleSummary]:
    articles: list[ArticleSummary] = []
    seen_urls: set[str] = set()

    for keyword in keywords:
        print(f"Searching Wikipedia for: {keyword}")
        titles = search_wikipedia(keyword, results_per_keyword, timeout)
        for title in titles:
            summary = fetch_summary(title, timeout)
            if summary is None or summary.url in seen_urls:
                continue
            seen_urls.add(summary.url)
            articles.append(summary)
            print(f"  Collected: {summary.title}")

    return articles


def write_dataset(records: Iterable[ArticleSummary], dataset_file) -> int:
    count = 0
    with dataset_file.open("w", encoding="utf-8") as handle:
        for record in records:
            payload = {
                "title": record.title,
                "url": record.url,
                "raw_text": record.raw_text,
            }
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
            count += 1
    return count


def main() -> None:
    settings = load_settings()
    ensure_runtime_directories(settings)

    keywords = load_keywords(settings.keywords_file)
    articles = collect_articles(
        keywords=keywords,
        results_per_keyword=settings.wiki_results_per_keyword,
        timeout=settings.wiki_request_timeout,
    )
    written = write_dataset(articles, settings.dataset_file)

    print(f"Wrote {written} article summaries to {settings.dataset_file}")


if __name__ == "__main__":
    main()
