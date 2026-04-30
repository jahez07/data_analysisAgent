from langchain_ollama import ChatOllama

model = ChatOllama(
    model="llama3.1:8b",
    temperature=0
)

messages = [
    (
        "system",
        "You are a helpful assistant that translates English to French. Translate the user sentence.",
    ),
    ("human", "I love programming."),
]
ai_msg = model.invoke(messages)
print(ai_msg)