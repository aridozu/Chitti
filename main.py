from agent.gpt_module import ask_gpt
import json
import os
from datetime import datetime
import pyttsx3
import speech_recognition as sr

engine = pyttsx3.init()

chat_history_file = "chat_log.json"
chat_history = [{"role": "system", "content": "You are a helpful assistant."}]
last_reply = ""


# ✅ --- FUNCTION FOR GRADIO & REUSE ---
def get_response(user_message):
    """
    Returns a chatbot reply (for Gradio or other apps).
    Uses the same chat history as CLI.
    """
    global chat_history
    chat_history.append({"role": "user", "content": user_message})
    reply = ask_gpt(user_message, chat_history)
    chat_history.append({"role": "assistant", "content": reply})
    return reply


# ✅ --- CLI ASSISTANT (Runs Only When Main is Executed Directly) ---
def run_cli():
    global chat_history, last_reply

    print("🤖 AI Assistant")
    choice = input("Start new session (/new) or load previous chat (/load)? ").strip().lower()

    if choice == "/load" and os.path.exists(chat_history_file):
        with open(chat_history_file, "r") as f:
            chat_history = json.load(f)
        print("🔄 Loaded previous chat.")
    else:
        chat_history = [{"role": "system", "content": "You are a helpful assistant."}]
        print("🆕 Started new chat.")

    print("\nType '/exit' to quit, '/clear' to reset, '/save' to save, '/speak' to read aloud, '/voice' for voice input.\n")

    while True:
        user_input = input("You: ").strip()

        # --- COMMANDS ---
        if user_input.lower() in ["/exit", "exit"]:
            print("Goodbye!")
            break

        elif user_input.lower() == "/clear":
            chat_history = [{"role": "system", "content": "You are a helpful assistant."}]
            print("✅ Chat history cleared.")
            continue

        elif user_input.lower() == "/save":
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"chat_log_{timestamp}.json"
            with open(filename, "w") as f:
                json.dump(chat_history, f, indent=4)
            print(f"✅ Chat saved as {filename}.")
            continue

        elif user_input.lower() == "/speak":
            if last_reply:
                engine.say(last_reply)
                engine.runAndWait()
            else:
                print("⚠️ Nothing to speak yet.")
            continue

        elif user_input.lower() == "/voice":
            try:
                recognizer = sr.Recognizer()
                with sr.Microphone() as source:
                    print("🎤 Listening...")
                    audio = recognizer.listen(source)

                user_input = recognizer.recognize_google(audio)
                print(f"You (voice): {user_input}")

            except sr.UnknownValueError:
                print("⚠️ Sorry, I couldn't understand your voice.")
                continue
            except sr.RequestError:
                print("⚠️ Speech recognition service unavailable.")
                continue

        # --- CHATBOT RESPONSE ---
        reply = get_response(user_input)
        print(f"Assistant: {reply}")
        last_reply = reply


# ✅ --- ONLY RUN CLI IF THIS FILE IS EXECUTED DIRECTLY ---
if __name__ == "__main__":
    run_cli()




