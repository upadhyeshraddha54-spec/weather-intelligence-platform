import os

from dotenv import load_dotenv
from transformers import pipeline

load_dotenv()

pipe = pipeline(
    "text-generation",
    model="Qwen/Qwen2.5-1.5B-Instruct",
    device_map="auto"
)


def ask_llm(prompt):

    messages = [
        {
            "role": "user",
            "content": prompt
        }
    ]

    output = pipe(
        messages,
        max_new_tokens=300,
        temperature=0.2
    )

    return output[0]["generated_text"][-1]["content"]