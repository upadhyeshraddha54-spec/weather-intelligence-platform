from langchain_core.tools import tool

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vectorstore = FAISS.load_local(
    "weather_vector_db",
    embeddings,
    allow_dangerous_deserialization=True
)


@tool
def search_weather_knowledge(query: str) -> str:
    """
    Search official weather and climate documents
    for relevant guidance and information.
    """

    docs = vectorstore.similarity_search(
        query,
        k=3
    )

    if not docs:
        return "No relevant information was found."

    results = []

    for doc in docs:
        source = doc.metadata.get(
            "source",
            "Unknown source"
        )

        results.append(
            f"Source: {source}\n"
            f"Content:\n{doc.page_content}"
        )

    return "\n\n---\n\n".join(results)