import os
import json

from dotenv import load_dotenv
from groq import Groq

from src.agent.tools import weather_tool, risk_tool
from src.agent.rag_tool import search_weather_knowledge


load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


# Tools available to the agent
AVAILABLE_TOOLS = {
    "weather_tool": weather_tool,
    "risk_tool": risk_tool,
    "search_weather_knowledge": search_weather_knowledge
}


# Groq tool definitions
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "weather_tool",
            "description": "Get current weather and air quality observations for a city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name, for example Pune"
                    }
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "risk_tool",
            "description": "Assess current weather and air quality risks for a city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name, for example Pune"
                    }
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_weather_knowledge",
            "description": "Search official weather and climate documents for relevant guidance.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Weather or climate knowledge to search for"
                    }
                },
                "required": ["query"]
            }
        }
    }
]


def run_weather_agent(question):

    messages = [
        {
            "role": "system",
            "content": """
You are a Weather Intelligence Decision Support Agent.

Your job is to investigate weather situations using available tools.

You can:
1. Get current weather and AQI.
2. Assess weather and air-quality risks.
3. Search official weather and climate knowledge.

Use tools when necessary.

Do not invent observations.
Do not claim that an official warning exists unless the tool results support it.

After gathering enough information, provide a concise professional decision-support response.
"""
        },
        {
            "role": "user",
            "content": question
        }
    ]

    # Agent loop
    for _ in range(5):

        response = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            temperature=0.2
        )

        message = response.choices[0].message

        # No more tool calls → final answer
        if not message.tool_calls:

            return message.content

        # Add assistant's tool-call message
        messages.append(message)

        # Execute requested tools
        for tool_call in message.tool_calls:

            tool_name = tool_call.function.name

            arguments = json.loads(
                tool_call.function.arguments
            )

            print(f"\n🔧 Agent calling: {tool_name}")
            print(f"Arguments: {arguments}")

            if tool_name not in AVAILABLE_TOOLS:

                result = "Tool not available."

            else:

                try:
                    result = AVAILABLE_TOOLS[tool_name].invoke(
                        arguments
                    )

                except Exception as e:

                    result = f"Tool error: {str(e)}"

            # Send tool result back to Groq
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result)
                }
            )

    return "The agent could not complete the analysis."


if __name__ == "__main__":

    question = input(
        "\nAsk the Weather Intelligence Agent: "
    )

    answer = run_weather_agent(question)

    print("\n================================")
    print("🤖 WEATHER INTELLIGENCE AGENT")
    print("================================")

    print(answer)
    