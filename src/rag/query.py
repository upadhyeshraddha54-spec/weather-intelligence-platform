import os
from dotenv import load_dotenv
from groq import Groq

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Load environment variables
load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Load embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Load FAISS vector database
vectorstore = FAISS.load_local(
    "weather_vector_db",
    embeddings,
    allow_dangerous_deserialization=True
)

print("Weather RAG Assistant Started!")
print("Type 'exit' to quit.\n")

while True:
    question = input("Ask: ")

    if question.lower() == "exit":
        break

    # Retrieve top 3 relevant chunks
    docs = vectorstore.similarity_search(question, k=3)

    context = "\n\n".join([doc.page_content for doc in docs])

    prompt = f"""
You are an AI Weather Assistant.

Answer ONLY using the information provided below.

Context:
{context}

Question:
{question}
"""

    response = client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    print("\nAnswer:\n")
    print(response.choices[0].message.content)
    print("\n" + "=" * 60 + "\n")