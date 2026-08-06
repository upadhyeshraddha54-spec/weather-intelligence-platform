import os
import requests
import streamlit as st
from dotenv import load_dotenv
from groq import Groq

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# --------------------------------------------------
# Load Environment Variables
# --------------------------------------------------

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# --------------------------------------------------
# Load Embeddings and FAISS Vector Database
# --------------------------------------------------

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vectorstore = FAISS.load_local(
    "weather_vector_db",
    embeddings,
    allow_dangerous_deserialization=True
)

# --------------------------------------------------
# Streamlit UI
# --------------------------------------------------

st.set_page_config(
    page_title="AI Weather Intelligence Platform",
    page_icon="🌦",
    layout="centered"
)

st.title("🌦 AI Weather Intelligence Platform")

st.write(
    "Predict temperature using Machine Learning and ask weather-related questions using an AI-powered RAG assistant."
)

st.divider()

# ==================================================
# MACHINE LEARNING PREDICTION
# ==================================================

st.header("🌡 Temperature Prediction")

humidity = st.number_input(
    "Humidity (%)",
    min_value=0.0,
    max_value=100.0,
    value=70.0
)

precip = st.number_input(
    "Precipitation (mm)",
    min_value=0.0,
    max_value=100.0,
    value=0.0
)

month = st.selectbox(
    "Month",
    list(range(1, 13))
)

day = st.slider(
    "Day",
    1,
    31,
    15
)

days = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6
}

day_name = st.selectbox(
    "Day of Week",
    list(days.keys())
)

dayofweek = days[day_name]

season_map = {
    "Winter": 0,
    "Summer": 1,
    "Monsoon": 2,
    "Post-Monsoon": 3
}

season_name = st.selectbox(
    "Season",
    list(season_map.keys())
)

season = season_map[season_name]

if st.button("Predict Temperature"):

    payload = {
        "humidity": humidity,
        "precip": precip,
        "month": month,
        "day": day,
        "dayofweek": dayofweek,
        "season": season
    }

    response = requests.post(
        "http://127.0.0.1:8000/predict",
        json=payload
    )

    if response.status_code == 200:

        prediction = response.json()

        st.metric(
            label="🌡 Predicted Temperature",
            value=f"{prediction['Predicted Temperature']} °C"
        )

    else:
        st.error("Prediction failed. Make sure the FastAPI server is running.")

# ==================================================
# RAG WEATHER ASSISTANT
# ==================================================

st.divider()

st.header("🤖 Weather AI Assistant")

question = st.text_input(
    "Ask anything about weather or climate:"
)

if st.button("Ask AI"):

    if question.strip() == "":
        st.warning("Please enter a question.")
    else:

        # Retrieve relevant chunks
        docs = vectorstore.similarity_search(
            question,
            k=3
        )

        context = "\n\n".join(
            [doc.page_content for doc in docs]
        )

        prompt = f"""
You are an AI Weather Assistant.

Answer ONLY using the information provided in the context below.

If the answer is not found in the context, reply:
"I couldn't find that information in the uploaded weather documents."

Context:
{context}

Question:
{question}
"""

        with st.spinner("Searching weather documents..."):

            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

        st.subheader("Answer")

        st.write(
            response.choices[0].message.content
        )