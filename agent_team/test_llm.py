
from llm_client import ask_llm

reply = ask_llm(
    system_prompt="You are a helpful Python assistant.",
    user_prompt="Reply with exactly: Groq connection successful."
)

print("Groq response:", reply)
