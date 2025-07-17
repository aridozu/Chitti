import gradio as gr
from agent.gpt_module import ask_gpt
import json
import pyttsx3
import speech_recognition as sr

engine = pyttsx3.init()
chat_history = [{"role": "system", "content": "You are a helpful assistant."}]
last_reply = ""


def process_message(message):
    global chat_history, last_reply
    reply = ask_gpt(message, chat_history)
    chat_history.append({"role": "user", "content": message})
    chat_history.append({"role": "assistant", "content": reply})
    last_reply = reply
    return reply


def update_chat_ui():
    formatted_chat = []
    for i in range(1, len(chat_history), 2):
        if i + 1 < len(chat_history):
            formatted_chat.append(
                {"role": "user", "content": chat_history[i]["content"]}
            )
            formatted_chat.append(
                {"role": "assistant", "content": chat_history[i + 1]["content"]}
            )
    return formatted_chat



def handle_text_input(user_message):
    if user_message.strip() == "":
        return update_chat_ui(), ""

    if user_message.lower() == "/clear":
        return clear_chat()

    reply = process_message(user_message)
    return update_chat_ui(), ""


def voice_input():
    try:
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("🎤 Listening...")
            audio = recognizer.listen(source)

        text = recognizer.recognize_google(audio)
        print(f"Voice Input: {text}")
        reply = process_message(text)
        return update_chat_ui(), f"🎤 You said: {text}\n🤖 {reply}"

    except sr.UnknownValueError:
        return update_chat_ui(), "⚠️ Sorry, I couldn't understand your voice."
    except sr.RequestError:
        return update_chat_ui(), "⚠️ Speech recognition service unavailable."


def speak_reply():
    if last_reply:
        engine.say(last_reply)
        engine.runAndWait()
        return update_chat_ui(), "🔊 Spoke the last reply."
    else:
        return update_chat_ui(), "⚠️ Nothing to speak yet."


def clear_chat():
    global chat_history, last_reply
    chat_history = [{"role": "system", "content": "You are a helpful assistant."}]
    last_reply = ""
    return [], "✅ Chat cleared."


# ✅ ---- Gradio UI ----
with gr.Blocks() as demo:
    gr.Markdown("## 🤖 AI Assistant with Voice & Speak")
    chatbot = gr.Chatbot(type="messages", height=400)
    msg = gr.Textbox(label="Type your message here and press Enter")

    with gr.Row():
        voice_btn = gr.Button("🎤 Voice Input")
        speak_btn = gr.Button("🔊 Speak Reply")
        clear_btn = gr.Button("🗑️ Clear Chat")

    status = gr.Label()

    msg.submit(handle_text_input, [msg], [chatbot, msg])
    voice_btn.click(voice_input, None, [chatbot, status])
    speak_btn.click(speak_reply, None, [chatbot, status])
    clear_btn.click(clear_chat, None, [chatbot, status])

demo.launch()

