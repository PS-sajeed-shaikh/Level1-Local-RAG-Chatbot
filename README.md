# Level1-Local-RAG

## Overview

`Level1-Local-RAG` is a local Retrieval-Augmented Generation (RAG) solution that demonstrates a complete knowledge-ingestion and question-answering workflow using:

- Wikipedia as the source system
- Ollama for local embeddings and local LLM inference
- ChromaDB for vector storage
- Streamlit for the user interface

The project is intentionally scoped as a Level 1 baseline. It prioritizes clarity, modularity, and reproducibility over optimization or advanced retrieval strategies.

## Purpose

This project exists to provide a simple, inspectable implementation of a local-first RAG pipeline. It is designed to help teams and learners understand the minimum components required to build a retrieval-backed chatbot without introducing external hosted APIs into the runtime path.

## Objectives

- establish a reproducible local RAG workflow
- separate data acquisition, ingestion, and chat interaction into clear modules
- preserve source traceability through metadata
- support grounded answers with source attribution
- provide a baseline that can be extended in later levels

## Scope

### In Scope

- keyword-driven topic definition through `keywords.xlsx`
- Wikipedia summary retrieval through the public Wikipedia API
- local embedding generation through Ollama
- local vector persistence through ChromaDB
- Streamlit-based question-answering interface
- environment validation through a health check

### Out of Scope

- enterprise security controls
- evaluation metrics and answer scoring
- document reranking
- hybrid retrieval
- full-article crawling
- multi-user state management
- production deployment automation

## Solution Summary

The solution operates in four logical stages:

1. topics are defined in `keywords.xlsx`
2. Wikipedia summaries are collected and stored in `dataset/data.txt`
3. the dataset is chunked, embedded, and indexed into ChromaDB
4. user questions are answered through retrieval plus local generation

## High-Level Architecture

```text
keywords.xlsx
    ->
app.scraper
    ->
dataset/data.txt
    ->
app.ingestion
    ->
chroma_db/
    ->
app.chatbot
```

## Repository Structure

```text
Level1-Local-RAG/
|-- app/
|   |-- chatbot.py
|   |-- config.py
|   |-- healthcheck.py
|   |-- ingestion.py
|   |-- rag.py
|   |-- scraper.py
|   `-- utils/
|       `-- keyword_utility.py
|-- dataset/
|   `-- data.txt
|-- .env
|-- .env.example
|-- keywords.xlsx
|-- README.md
`-- requirements.txt
```

## Module Responsibilities

## 1. Wikipedia Scraper

Implementation: [app/scraper.py](/C:/Users/MohammedsajeedShaikh/source/repos/Level1-Local-RAG/app/scraper.py)

Responsibilities:

- read topic keywords from the Excel input file
- search Wikipedia for relevant pages per keyword
- retrieve article summaries
- deduplicate records by source URL
- write the result set to `dataset/data.txt` in JSON Lines format

Input contract:

- file: `keywords.xlsx`
- required column: `Keyword`

Example:

| Keyword |
| --- |
| Artificial Intelligence |
| Machine Learning |
| Neural Networks |
| Deep Learning |
| Large Language Models |

Output contract:

- file: `dataset/data.txt`
- format: one JSON object per line

Example record:

```json
{
  "title": "Artificial intelligence",
  "url": "https://en.wikipedia.org/wiki/Artificial_intelligence",
  "raw_text": "Artificial intelligence (AI) is intelligence demonstrated by machines..."
}
```

## 2. Ingestion Pipeline

Implementation: [app/ingestion.py](/C:/Users/MohammedsajeedShaikh/source/repos/Level1-Local-RAG/app/ingestion.py)

Responsibilities:

- read dataset records from `dataset/data.txt`
- convert records into documents
- split long text into overlapping chunks
- generate embeddings through Ollama
- persist chunks and metadata into ChromaDB

Metadata stored per chunk:

- `source`
- `title`

Chunking strategy:

- chunk size: `1000`
- chunk overlap: `200`

Operational note:

- the vector database is rebuilt on each ingestion run

## 3. Chatbot Interface

Implementation: [app/chatbot.py](/C:/Users/MohammedsajeedShaikh/source/repos/Level1-Local-RAG/app/chatbot.py)

Responsibilities:

- accept user questions through Streamlit
- retrieve relevant chunks from ChromaDB
- assemble grounded context for the prompt
- invoke the local chat model
- display the answer and supporting sources

Expected response pattern:

```text
Artificial intelligence is the simulation of human intelligence in machines.

Sources:
- https://en.wikipedia.org/wiki/Artificial_intelligence
```

## 4. Health Check

Implementation: [app/healthcheck.py](/C:/Users/MohammedsajeedShaikh/source/repos/Level1-Local-RAG/app/healthcheck.py)

Validation coverage:

- configuration loading
- dataset availability
- vector database availability and chunk count
- embedding model readiness
- chat model readiness

## 5. Keyword Utility

Implementation: [app/utils/keyword_utility.py](/C:/Users/MohammedsajeedShaikh/source/repos/Level1-Local-RAG/app/utils/keyword_utility.py)

Purpose:

- generate a starter `keywords.xlsx` file for initial setup

Usage:

```powershell
python -m app.utils.keyword_utility
```

## Configuration Management

Configuration is provided through environment variables loaded from `.env`.

Reference values are available in [.env.example](/C:/Users/MohammedsajeedShaikh/source/repos/Level1-Local-RAG/.env.example).

### Reference Configuration

```env
DATASET_STORAGE_FOLDER=dataset
KEYWORDS_FILE=keywords.xlsx

WIKI_RESULTS_PER_KEYWORD=5
WIKI_REQUEST_TIMEOUT=20

CHUNK_SIZE=1000
CHUNK_OVERLAP=200

VECTOR_DB_COLLECTION=wiki_articles
VECTOR_DB_PATH=chroma_db

EMBEDDING_MODEL=nomic-embed-text

CHAT_MODEL_NAME=llama3.2
CHAT_MODEL_PROVIDER=ollama
CHAT_MODEL_TEMPERATURE=0

RETRIEVAL_TOP_K=3

CHAT_HISTORY_LIMIT=6
```

### Configuration Reference

`DATASET_STORAGE_FOLDER`

- target folder for generated dataset files

`KEYWORDS_FILE`

- path to the Excel keyword file

`WIKI_RESULTS_PER_KEYWORD`

- maximum number of Wikipedia search results evaluated per keyword

`WIKI_REQUEST_TIMEOUT`

- timeout in seconds for Wikipedia API calls

`CHUNK_SIZE`

- maximum characters stored per chunk

`CHUNK_OVERLAP`

- overlapping characters between adjacent chunks

`VECTOR_DB_COLLECTION`

- Chroma collection name

`VECTOR_DB_PATH`

- local Chroma persistence path

`EMBEDDING_MODEL`

- Ollama embedding model name

`CHAT_MODEL_NAME`

- Ollama chat model name

`CHAT_MODEL_PROVIDER`

- provider identifier, expected to be `ollama`

`CHAT_MODEL_TEMPERATURE`

- response temperature for the chat model

`RETRIEVAL_TOP_K`

- number of chunks retrieved for each question

`CHAT_HISTORY_LIMIT`

- number of recent chat messages included in prompt construction

## Runtime Prerequisites

The following prerequisites are required before execution:

- Python 3.10 or higher recommended
- `pip`
- Ollama installed and running
- locally available embedding and chat models

## Installation Procedure

Run all commands from the project root:

[Level1-Local-RAG](/C:/Users/MohammedsajeedShaikh/source/repos/Level1-Local-RAG)

### 1. Install Python Dependencies

Use the interpreter-qualified command on Windows:

```powershell
python -m pip install -r requirements.txt
```

### 2. Create the Runtime Configuration File

```powershell
Copy-Item .env.example .env
```

Then update `.env` if your locally available Ollama models differ from the reference configuration.

Example local override:

```env
EMBEDDING_MODEL=mxbai-embed-large:latest
CHAT_MODEL_NAME=llama3.2:3b
```

### 3. Validate Ollama Availability

```powershell
ollama list
```

### 4. Pull Required Models if Needed

Reference setup:

```powershell
ollama pull llama3.2
ollama pull nomic-embed-text
```

## Operational Runbook

### Step 1. Prepare Keywords

Generate a starter file if required:

```powershell
python -m app.utils.keyword_utility
```

Or create `keywords.xlsx` manually with the required `Keyword` column.

### Step 2. Generate the Dataset

```powershell
python -m app.scraper
```

Outcome:

- Wikipedia summaries are collected
- results are written to `dataset/data.txt`

### Step 3. Build the Vector Store

```powershell
python -m app.ingestion
```

Outcome:

- dataset records are loaded
- records are chunked
- embeddings are generated
- ChromaDB is populated in `chroma_db/`

### Step 4. Execute the Health Check

```powershell
python -m app.healthcheck
```

Expected validations:

- configuration
- dataset
- vector database
- embedding model
- chat model

### Step 5. Launch the Chatbot

Recommended command:

```powershell
python -m streamlit run app/chatbot.py
```

Alternative command if `streamlit` is already on `PATH`:

```powershell
streamlit run app/chatbot.py
```

## Example End-to-End Setup

```powershell
python -m pip install -r requirements.txt
Copy-Item .env.example .env
ollama pull llama3.2
ollama pull nomic-embed-text
python -m app.utils.keyword_utility
python -m app.scraper
python -m app.ingestion
python -m app.healthcheck
python -m streamlit run app/chatbot.py
```

## Sample User Questions

The following questions align with the starter keyword set:

- What is artificial intelligence?
- What is machine learning?
- What are neural networks?
- What is deep learning?
- What are large language models?
- How is machine learning different from deep learning?
- How are neural networks related to deep learning?
- What is the relationship between artificial intelligence and machine learning?
- What are large language models used for?
- Explain deep learning in simple terms and include sources.
- Compare machine learning and neural networks with sources.

## Design Rationale

## Local-First Architecture

Embeddings and response generation run through local Ollama models.

Rationale:

- no dependency on external hosted inference APIs
- improved privacy for local experimentation
- predictable development workflow
- no per-request API cost

## Explicit Topic Input

Topic scope is defined through `keywords.xlsx`.

Rationale:

- transparent data acquisition
- easy inspection and auditability
- reproducible pipeline input
- predictable scope control

## Fixed Chunking Strategy

Chunk size and overlap are fixed at `1000` and `200`.

Rationale:

- easy to understand
- low implementation complexity
- stable baseline for comparison in later iterations

## ChromaDB Selection

ChromaDB was chosen for this level because it is lightweight, local-friendly, and integrates cleanly with LangChain.

## Operational Constraints and Limitations

This project is a baseline implementation. The following limitations are currently accepted:

- only Wikipedia summaries are indexed
- ingestion rebuilds the vector database from scratch
- retrieval uses simple top-k similarity search
- no reranking is applied
- no formal answer-quality evaluation exists
- conversation memory is intentionally limited
- no production hardening or deployment automation is included

## Troubleshooting Guide

## `pip install -r requirements.txt` fails

Use:

```powershell
python -m pip install -r requirements.txt
```

Cause:

- `pip` may point to a different Python interpreter than the active runtime

## `ollama._types.ResponseError: model "... " not found`

Cause:

- the configured model in `.env` is not available in the local Ollama registry

Validation:

```powershell
ollama list
```

Resolution options:

1. pull the missing model
2. update `.env` to reference a model that already exists locally

Example:

```powershell
ollama pull nomic-embed-text
```

Or:

```env
EMBEDDING_MODEL=mxbai-embed-large:latest
CHAT_MODEL_NAME=llama3.2:3b
```

## `streamlit` is not recognized in PowerShell

Use:

```powershell
python -m streamlit run app/chatbot.py
```

Cause:

- the Python `Scripts` directory is not on the PowerShell `PATH`

Example path:

```text
C:\Users\MohammedsajeedShaikh\AppData\Local\Python\pythoncore-3.14-64\Scripts
```

## Health Check Fails on Vector Database Connectivity

Likely causes:

- ingestion has not been executed
- ingestion failed before writing chunks
- `.env` points to the wrong `VECTOR_DB_PATH`

## Chatbot Returns `I don't know.`

Likely causes:

- the topic is outside the indexed keyword scope
- the dataset does not contain enough relevant summary content
- ingestion was not rerun after keyword changes
- retrieval settings are too conservative for the question

## Roadmap

Potential Level 2 improvements include:

- full-article ingestion
- hybrid retrieval
- reranking
- evaluation metrics
- richer memory management
- chunk preview in answers
- multiple source systems beyond Wikipedia

## Conclusion

`Level1-Local-RAG` provides a clean enterprise-style reference implementation for a local RAG pipeline. It isolates each core responsibility into a distinct module and keeps the full flow explicit:

- define topics
- acquire source content
- build the vector index
- validate the environment
- answer questions with retrieval-backed generation

This makes it a strong baseline for demonstration, learning, and incremental extension into more advanced RAG capabilities.
