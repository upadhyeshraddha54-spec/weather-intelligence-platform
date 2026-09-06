from fastapi import FastAPI

app = FastAPI(
    title="Weather Intelligence Platform API",
    description="AI-Powered Multi-Agent Weather Intelligence Decision Support Platform",
    version="1.0.0"
)

@app.get("/")
def home():
    return {
        "message": "Weather Intelligence Platform API is running!"
    }