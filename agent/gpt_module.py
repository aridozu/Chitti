import os
import requests

# ✅ Try environment variable first (for Hugging Face), else fallback to hardcoded key for local use
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")

def ask_gpt(prompt, chat_history=None):
    """
    Sends a message to Groq's LLaMA model and returns the response.
    Works for both CLI and Gradio.
    """
    if not GROQ_API_KEY or not GROQ_API_KEY.startswith("gsk_"):
        return "⚠️ Invalid or missing API Key. Please check your GROQ_API_KEY."

    if chat_history is None:
        chat_history = [{"role": "system", "content": "You are a helpful assistant."}]

    chat_history.append({"role": "user", "content": prompt})

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama3-8b-8192",
        "messages": chat_history
    }

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=data
    )

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"].strip()
    else:
        return f"⚠️ API Error {response.status_code}: {response.text}"

