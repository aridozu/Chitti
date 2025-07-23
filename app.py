import os
import json
import random
import threading
import gradio as gr
from dotenv import load_dotenv
from groq import Groq
from voice_utils import listen_voice, speak_text
from playsound import playsound

# ✅ Load API Key
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("❌ GROQ_API_KEY is missing. Check your .env file.")
else:
    print("✅ GROQ_API_KEY loaded successfully.")

client = Groq(api_key=GROQ_API_KEY)

# ✅ Chat log file (Auto delete old logs on restart)
CHAT_LOG_FILE = "chat_log.json"
if os.path.exists(CHAT_LOG_FILE):
    os.remove(CHAT_LOG_FILE)

# ✅ Boothulu (Savage Replies)
with open("boothulu.json", "r", encoding="utf-8") as f:
    BOOTHULU = json.load(f)

# ✅ Detect Language
def detect_language(text):
    telugu_chars = sum(1 for c in text if "\u0C00" <= c <= "\u0C7F")
    hindi_chars = sum(1 for c in text if "\u0900" <= c <= "\u097F")
    if telugu_chars > hindi_chars and telugu_chars > 3:
        return "telugu"
    elif hindi_chars > telugu_chars and hindi_chars > 3:
        return "hindi"
    else:
        return "english"

# ✅ Savage Reply
def get_savage_reply(language):
    return random.choice(BOOTHULU.get(language, BOOTHULU["english"]))

# ✅ Load chat history
def load_chat_history():
    return []  # always start fresh

# ✅ Save chat history
def save_chat_history(history):
    with open(CHAT_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4)

# ✅ Typing Sound Function
def play_typing_sound():
    try:
        playsound("sounds/typing.mp3", block=False)
    except Exception as e:
        print(f"⚠️ Typing sound error: {e}")

# ✅ Chat Function
def chat_with_ai(message, history):
    try:
        history.append({"role": "user", "content": message})

        # ✅ Savage Mode if aggressive words detected
        aggressive_words = ["puka", "gudda", "fuck", "madarchod", "lodu", "pani ledu", "deng", "chutiya"]
        if any(word in message.lower() for word in aggressive_words):
            lang = detect_language(message)
            savage_reply = get_savage_reply(lang)
            history.append({"role": "assistant", "content": savage_reply})
            save_chat_history(history)
            return history, ""

        # ✅ Normal AI mode (Only send last 10 messages for context)
        groq_history = [{"role": msg["role"], "content": msg["content"]}
                        for msg in history[-10:]]

        # ✅ Typing Sound
        threading.Thread(target=play_typing_sound).start()

        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=groq_history
        )
        response = completion.choices[0].message.content
        history.append({"role": "assistant", "content": response})
        save_chat_history(history)
        return history, ""

    except Exception as e:
        history.append({"role": "assistant", "content": f"⚠️ API Error: {str(e)}"})
        save_chat_history(history)
        return history, ""

# ✅ Voice Input
def voice_input(history):
    user_input = listen_voice()
    if user_input:
        return chat_with_ai(user_input, history)
    return history, ""

# ✅ Speak Last Response
def speak_last(history):
    if history and history[-1]["role"] == "assistant":
        speak_text(history[-1]["content"], villain_mode=True)
    return history

# ✅ Red & Black Animated Villain Theme
with gr.Blocks(css="""
    body {background-color: #000 !important; color: #FF0000 !important; font-family: 'Courier New', monospace;}
    .gradio-container {background-color: #000 !important; color: #FF0000 !important; animation: pulse-bg 4s infinite alternate;}
    .gr-chatbot {background-color: #000 !important; color: #FF0000 !important; border: 2px solid #FF0000 !important; box-shadow: 0px 0px 12px #FF0000; animation: glow 2s infinite alternate;}
    .gr-chatbot .message.user {background-color: #111 !important; color: #FF3333 !important; border: 1px solid #FF0000 !important; box-shadow: 0px 0px 6px #FF0000;}
    .gr-chatbot .message.bot {background-color: #000 !important; color: #FF0000 !important; border: 1px solid #990000 !important; text-shadow: 0px 0px 8px #FF0000; animation: flicker 1.5s infinite alternate;}
    .gr-button {background-color: #FF0000 !important; color: #000 !important; border: 2px solid #FF0000 !important; font-weight: bold; box-shadow: 0px 0px 8px #FF0000; animation: glow 2s infinite alternate;}
    .gr-button:hover {background-color: #990000 !important; color: #FFF !important; box-shadow: 0px 0px 15px #FF0000;}
    .gr-textbox {background-color: #111 !important; color: #FF0000 !important; border: 2px solid #FF0000 !important; box-shadow: 0px 0px 6px #FF0000;}
    h1, h2, h3, h4, h5, h6 {color: #FF0000 !important; text-shadow: 0px 0px 12px #FF0000; animation: flicker 2s infinite alternate;}
    @keyframes glow {from { box-shadow: 0px 0px 5px #FF0000; } to { box-shadow: 0px 0px 15px #FF0000; }}
    @keyframes flicker {0% { opacity: 1; } 50% { opacity: 0.8; } 100% { opacity: 1; }}
    @keyframes pulse-bg {from { background-color: #000; } to { background-color: #110000; }}
""") as demo:

    gr.Markdown("## 😈 Chitti - The Most Savage AI on Earth")

    chatbot = gr.Chatbot(value=load_chat_history(), label="Savage Chitti", type="messages")
    txt = gr.Textbox(placeholder="Type your message...", show_label=False)

    with gr.Row():
        submit_btn = gr.Button("Send")
        voice_btn = gr.Button("🎤 Voice Input")
        speak_btn = gr.Button("🔊 Villain Voice")

    submit_btn.click(chat_with_ai, [txt, chatbot], [chatbot, txt])
    txt.submit(chat_with_ai, [txt, chatbot], [chatbot, txt])
    voice_btn.click(voice_input, [chatbot], [chatbot])
    speak_btn.click(speak_last, [chatbot], [chatbot])

demo.launch()
