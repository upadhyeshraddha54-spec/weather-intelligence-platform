from src.llm.llm import ask_llm

question = input(">>> ")

answer = ask_llm(question)

print(answer)