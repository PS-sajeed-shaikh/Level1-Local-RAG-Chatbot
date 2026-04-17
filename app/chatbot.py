from __future__ import annotations

import streamlit as st
from langchain_core.messages import HumanMessage, SystemMessage

from app.config import load_settings
from app.rag import build_chat_model, build_embeddings, build_vector_store, unique_sources


SYSTEM_PROMPT = """You are a grounded retrieval-augmented assistant.
Answer only from the supplied context.
If the context is insufficient, say "I don't know."
Keep the answer concise and factual."""


@st.cache_resource
def get_backend():
    settings = load_settings()
    embeddings = build_embeddings(settings)
    vector_store = build_vector_store(settings, embeddings)
    llm = build_chat_model(settings)
    return settings, vector_store, llm


def format_history(messages: list[dict], limit: int) -> str:
    if not messages:
        return "No prior conversation."

    recent_messages = messages[-limit:]
    lines = [f"{message['role'].title()}: {message['content']}" for message in recent_messages]
    return "\n".join(lines)


def response_text(message) -> str:
    content = getattr(message, "content", "")
    if isinstance(content, str):
        return content.strip()
    return str(content).strip()


def build_answer(question: str, history: list[dict]) -> str:
    settings, vector_store, llm = get_backend()

    documents = vector_store.similarity_search(question, k=settings.retrieval_top_k)
    if not documents:
        return "I don't know."

    context = "\n\n".join(
        [
            f"Title: {document.metadata.get('title', 'Unknown')}\n"
            f"Source: {document.metadata.get('source', 'Unknown')}\n"
            f"Content: {document.page_content}"
            for document in documents
        ]
    )

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(
            content=(
                f"Conversation history:\n{format_history(history, settings.chat_history_limit)}\n\n"
                f"Question:\n{question}\n\n"
                f"Retrieved context:\n{context}\n\n"
                "Provide a grounded answer based only on the retrieved context."
            )
        ),
    ]

    answer = response_text(llm.invoke(messages))
    sources = unique_sources(documents)

    if not sources or answer.lower() == "i don't know.":
        return "I don't know."

    return answer + "\n\nSources:\n" + "\n".join(f"- {source}" for source in sources)


def main() -> None:
    settings, _, _ = get_backend()

    st.set_page_config(page_title="Level1 Local RAG")
    st.title("Level1 Local RAG")
    st.caption("Wikipedia summaries + Ollama embeddings + ChromaDB retrieval")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_question = st.chat_input("Ask a question about the ingested Wikipedia topics")

    if not user_question:
        return

    st.session_state.messages.append({"role": "user", "content": user_question})
    with st.chat_message("user"):
        st.markdown(user_question)

    try:
        with st.chat_message("assistant"):
            with st.spinner("Retrieving context and generating answer..."):
                answer = build_answer(user_question, st.session_state.messages[:-1])
                st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
    except Exception as exc:
        st.error(
            "Failed to generate an answer. Run `python -m app.healthcheck` and confirm "
            f"the vector store and Ollama models are ready.\n\nError: {exc}"
        )


if __name__ == "__main__":
    main()
