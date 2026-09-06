"""
RAG Tool — searches the weather knowledge vector database.

Uses lazy initialization so importing this module never crashes on startup,
even in environments without network access to HuggingFace.
"""
import os
import logging

from langchain_core.tools import tool

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lazy state
# ---------------------------------------------------------------------------

_embeddings = None
_vectorstore = None
_rag_available = None   # None = untested, True/False = known


def _get_vectorstore():
    """
    Load the FAISS vectorstore exactly once, using the local model cache.
    Returns None (never raises) if anything fails.
    """
    global _embeddings, _vectorstore, _rag_available

    if _rag_available is not None:
        return _vectorstore

    try:
        # Force offline so no network call is made for the embeddings model.
        os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
        os.environ.setdefault("HF_DATASETS_OFFLINE", "1")

        from langchain_huggingface import HuggingFaceEmbeddings
        from langchain_community.vectorstores import FAISS

        _embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        # Resolve vectorstore path relative to the project root.
        project_root = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        db_path = os.path.join(project_root, "weather_vector_db")

        if not os.path.isdir(db_path):
            logger.warning(
                "RAG: weather_vector_db not found at %s — "
                "RAG queries will be unavailable.",
                db_path,
            )
            _rag_available = False
            return None

        _vectorstore = FAISS.load_local(
            db_path,
            _embeddings,
            allow_dangerous_deserialization=True,
        )
        _rag_available = True
        logger.info("RAG: vectorstore loaded from %s", db_path)

    except Exception as exc:
        logger.warning("RAG: vectorstore could not be loaded — %s", exc)
        _rag_available = False
        _vectorstore = None

    return _vectorstore


# ---------------------------------------------------------------------------
# LangChain tool
# ---------------------------------------------------------------------------

@tool
def search_weather_knowledge(query: str) -> str:
    """
    Search official weather and climate documents
    for relevant guidance and information.
    """
    vs = _get_vectorstore()

    if vs is None:
        return (
            "Weather knowledge base is currently unavailable. "
            "RAG search could not be performed."
        )

    try:
        docs = vs.similarity_search(query, k=3)
    except Exception as exc:
        logger.warning("RAG search failed: %s", exc)
        return "Weather knowledge base search failed."

    if not docs:
        return "No relevant information was found in the knowledge base."

    results = []
    for doc in docs:
        source = doc.metadata.get("source", "Unknown source")
        results.append(f"Source: {source}\nContent:\n{doc.page_content}")

    return "\n\n---\n\n".join(results)