import os
import json
import datetime
import random
import pyttsx3
import speech_recognition as sr
import gradio as gr
from groq import Groq
from dotenv import load_dotenv
from ddgs import DDGS

# ✅ Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    print("⚠️ GROQ_API_KEY not found in environment.")
else:
    print("✅ GROQ_API_KEY loaded successfully.")

client = Groq(api_key=GROQ_API_KEY)
search_engine = DDGS()

# ✅ Chat History File
CHAT_HISTORY_FILE = "chat_history.json"

# ✅ Day-wise colors (7 colors for 7 days)
DAY_COLORS = [
    "#FFB3BA", "#FFDFBA", "#FFFFBA", "#BAFFC9",
    "#BAE1FF", "#E3BAFF", "#FFBAE1"
]

# ✅ Text-to-Speech
engine = pyttsx3.init()
engine.setProperty("rate", 175)

def speak_text(text):
    engine.say(text)
    engine.runAndWait()

def voice_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening...")
        audio = recognizer.listen(source)
        try:
            return recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            return "Sorry, I couldn't understand that."
        except sr.RequestError:
            return "Speech service unavailable."

# ✅ Save Chat History
def save_chat_history(history):
    with open(CHAT_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

# ✅ Load Chat History
def load_chat_history():
    if os.path.exists(CHAT_HISTORY_FILE):
        with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# ✅ Format Chat for Gradio (messages format)
def format_chat_for_ui(chat_history):
    formatted = []
    for msg in chat_history:
        if msg["role"] == "date":
            formatted.append({
                "role": "assistant",
                "content": f"📅 **{msg['content']}**"
            })
        else:
            formatted.append(msg)
    return formatted

# ✅ Add Date Header (only once per day)
def add_daily_date_if_needed(history):
    today = datetime.date.today().strftime("%Y-%m-%d")
    if not history or history[-1].get("role") != "date" or history[-1].get("content") != today:
        color = random.choice(DAY_COLORS)
        history.append({"role": "date", "content": today, "color": color})
    return history

# ✅ AI Response Function (with DuckDuckGo integration)
def chatbot_response(message, history):
    history = load_chat_history()
    history = add_daily_date_if_needed(history)

    # ✅ Search if starts with "search:"
    if message.lower().startswith("search:"):
        query = message[7:].strip()
        results = list(search_engine.text(query, max_results=3))
        if results:
            answer = "\n\n".join([f"🔗 [{r['title']}]({r['href']})\n{r['body']}" for r in results])
        else:
            answer = "No results found."
    else:
        try:
            response = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "system", "content": "You are Savage Chitti, a witty assistant."}] +
                         [{"role": msg["role"], "content": msg["content"]}
                          for msg in history if msg["role"] in ["user", "assistant"]] +
                         [{"role": "user", "content": message}],
                temperature=0.7
            )
            answer = response.choices[0].message.content.strip()
        except Exception as e:
            answer = f"⚠️ API Error: {str(e)}"

    timestamp = datetime.datetime.now().strftime("%H:%M")
    history.append({"role": "user", "content": f"{message}  \n⏰ {timestamp}"})
    history.append({"role": "assistant", "content": f"{answer}  \n⏰ {timestamp}"})
    save_chat_history(history)

    return format_chat_for_ui(history), ""

# ✅ Clear Only Current Session (Keeps File)
def clear_session():
    return []

# ✅ Read Last Response
def speak_last_response(history):
    if history and isinstance(history[-1], dict) and history[-1]["role"] == "assistant":
        speak_text(history[-1]["content"].replace("⏰", ""))

# ✅ UI
with gr.Blocks(css="""
body {background-color: #F8F9FB;}
.gradio-container {max-width: 850px; margin: auto;}
#col-container {display: flex; gap: 10px;}
.date-header {font-weight: bold; padding: 6px; border-radius: 6px; text-align: center;}
button {border-radius: 8px; font-weight: bold;}
""") as demo:
    gr.Markdown("## 🤖 Savage Chitti (with Internet Search & Timestamps)")
    chatbot = gr.Chatbot(value=format_chat_for_ui(load_chat_history()), label="Savage Chitti", type="messages")

    with gr.Row():
        msg = gr.Textbox(placeholder="Type a message or 'search: your query'...", scale=4)
        send_btn = gr.Button("Send", scale=1)
        speak_btn = gr.Button("🔊 Speak Last", scale=1)
        voice_btn = gr.Button("🎤 Voice", scale=1)
        clear_btn = gr.Button("🗑️ Clear Session", scale=1)

    send_btn.click(chatbot_response, [msg, chatbot], [chatbot, msg])
    msg.submit(chatbot_response, [msg, chatbot], [chatbot, msg])
    voice_btn.click(lambda h: chatbot_response(voice_input(), h), [chatbot], chatbot)
    speak_btn.click(speak_last_response, [chatbot], None)
    clear_btn.click(clear_session, None, chatbot)

demo.launch()
