import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime
import pyttsx3
import speech_recognition as sr
import requests
import wikipedia
import threading
import json
import os
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()

# ==== CONFIG ====
API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama3-70b-8192"
API_KEY = os.getenv("OPENAI_API_KEY")
CHAT_FILE = "chat_log.json"

# ==== TEXT-TO-SPEECH ====
engine = pyttsx3.init()
def speak_text(text):
    engine.say(text)
    engine.runAndWait()

# ==== SPEECH-TO-TEXT ====
def get_voice_input():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening...")
        audio = r.listen(source)
    try:
        return r.recognize_google(audio)
    except sr.UnknownValueError:
        return "Sorry, I didn't catch that."
    except sr.RequestError:
        return "Speech recognition service is down."

# ==== GPT FUNCTION ====
def ask_gpt(messages):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.7
    }
    response = requests.post(API_URL, headers=headers, json=data)
    print("Status Code:", response.status_code)
    print("Raw Response:", response.text)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

# ==== GUI SETUP ====
root = tk.Tk()
root.title("AI Assistant Bot")
root.geometry("600x500")

chat_display = scrolledtext.ScrolledText(root, wrap=tk.WORD, state=tk.DISABLED)
chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

entry = tk.Entry(root)
entry.pack(padx=10, pady=(0, 10), fill=tk.X)

context_mode = tk.StringVar()
context_mode.set("continue")

chat_history = []
last_response = {"text": ""}

if os.path.exists(CHAT_FILE):
    with open(CHAT_FILE, "r") as f:
        chat_history = json.load(f)
else:
    chat_history.append({"role": "system", "content": "You are a helpful assistant."})

# ==== APPEND MESSAGE ====
def append_message(sender, message, timestamp=None):
    chat_display.config(state=tk.NORMAL)
    if timestamp:
        chat_display.insert(tk.END, f"{sender} {timestamp}: {message}\n\n")
    else:
        chat_display.insert(tk.END, f"{sender}: {message}\n\n")
    chat_display.config(state=tk.DISABLED)
    chat_display.yview(tk.END)

# ==== MAIN FUNCTION ====
def send_message():
    user_input = entry.get().strip()
    if not user_input:
        return

    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    append_message("You", f"{user_input}", timestamp)
    chat_history.append({"role": "user", "content": user_input})
    entry.delete(0, tk.END)

    # ==== COMMANDS ====
    if user_input.lower() in ["/exit", "exit"]:
        root.destroy()
        return

    elif user_input.lower() == "/clear":
        chat_display.config(state=tk.NORMAL)
        chat_display.delete(1.0, tk.END)
        chat_display.config(state=tk.DISABLED)
        chat_history.clear()
        chat_history.append({"role": "system", "content": "You are a helpful assistant."})
        return

    elif user_input.lower() == "/save":
        with open(CHAT_FILE, "w") as f:
            json.dump(chat_history, f, indent=4)
        append_message("Assistant", "\u2705 Chat saved.")
        return

    elif user_input.lower() == "/speak":
        if last_response["text"]:
            threading.Thread(target=speak_text, args=(last_response["text"],)).start()
        else:
            append_message("Assistant", "There's no response to speak.")
        return

    elif user_input.lower() == "/voice":
        voice_input = get_voice_input()
        timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        append_message("You (voice)", voice_input, timestamp)
        entry.insert(0, voice_input)
        send_message()
        return

    elif user_input.startswith("/wiki"):
        query = user_input[len("/wiki"):].strip()
        if not query:
            append_message("Assistant", "Please enter a topic after /wiki.")
            return
        try:
            summary = wikipedia.summary(query, sentences=3)
            append_message("Assistant", summary)
            last_response["text"] = summary
        except wikipedia.exceptions.DisambiguationError as e:
            append_message("Assistant", f"Ambiguous query. Try: {', '.join(e.options[:5])}")
        except wikipedia.exceptions.PageError:
            append_message("Assistant", "Sorry, I couldn't find that topic.")
        except Exception as e:
            append_message("Assistant", f"Error fetching from Wikipedia: {e}")
        return

    # ==== GPT RESPONSE ====
    def generate():
        try:
            messages = chat_history if context_mode.get() == "continue" else [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_input}
            ]
            reply = ask_gpt(messages)
            timestamp_reply = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
            append_message("Assistant", reply, timestamp_reply)
            chat_history.append({"role": "assistant", "content": reply})
            last_response["text"] = reply
        except Exception as e:
            append_message("Assistant", f"Error: {e}")

    threading.Thread(target=generate).start()

# ==== BIND + BUTTON ====
entry.bind("<Return>", lambda event: send_message())

button = tk.Button(root, text="Send", command=send_message)
button.pack(pady=(0, 10))

# ==== START GUI ====
append_message("🤖", "Chitti THE AI Bot! Type '/exit' to quit, '/clear' to reset, '/save' to save chat, '/speak' to read response, '/voice' for voice input, '/wiki <topic>' for Wikipedia.")
print("Launching GUI...")
root.mainloop()
