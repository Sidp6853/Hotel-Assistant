from langchain_ollama import ChatOllama

# Initialize LLM
llm = ChatOllama(
    model="llama3.2:3b",
    temperature=0.3
)

# Simple prompt as string
prompt = "You are a friendly assistant. Answer this in 2 sentences: What is the capital of France?"

# Run the model
response = llm.invoke(prompt)

print("Response from Ollama:\n")
print(response.content)
sssss