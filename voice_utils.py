import speech_recognition as sr
import pyttsx3
import threading

# ✅ Initialize TTS engine (only once)
engine = pyttsx3.init()
engine.setProperty("rate", 175)
engine.setProperty("volume", 1.0)

def listen_voice():
    """Capture voice input and return as text"""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
    try:
        text = r.recognize_google(audio)
        print(f"✅ You said: {text}")
        return text
    except sr.UnknownValueError:
        print("❌ Could not understand audio")
        return None
    except sr.RequestError as e:
        print(f"⚠️ Voice recognition error: {e}")
        return None

def _speak(text):
    """Private function to handle TTS in a separate thread"""
    engine.say(text)
    engine.runAndWait()

def speak_text(text):
    """Speak text in background without blocking the UI"""
    threading.Thread(target=_speak, args=(text,), daemon=True).start()
