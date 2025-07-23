import os
import requests
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("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")

def ask_gpt(prompt, chat_history=None):
    """
    Sends a message to Groq's LLaMA model and returns the response.
    """
    if not GROQ_API_KEY:
        return "⚠️ GROQ_API_KEY is missing. Check your .env file."

    if chat_history is None:
        chat_history = [{"role": "system", "content": "You are a helpful assistant."}]

    # ✅ Clean messages (Groq doesn't support extra metadata)
    clean_history = []
    for msg in chat_history:
        clean_history.append({"role": msg["role"], "content": msg["content"]})

    clean_history.append({"role": "user", "content": prompt})

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama3-8b-8192",
        "messages": clean_history
    }

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=data
    )

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"].strip()
    else:
        return f"⚠️ API Error: {response.text}"
