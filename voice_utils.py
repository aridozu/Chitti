import pyttsx3
from langdetect import detect
import speech_recognition as sr

# ✅ Initialize Text-to-Speech Engine
engine = pyttsx3.init()

# ✅ Calm Normal Voice
def set_calm_voice(language="en"):
    voices = engine.getProperty('voices')
    for voice in voices:
        if language == "te" and "telugu" in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break
        elif language == "hi" and ("hindi" in voice.name.lower() or "india" in voice.name.lower()):
            engine.setProperty('voice', voice.id)
            break
        elif language == "en" and ("english" in voice.name.lower() or "us" in voice.name.lower()):
            engine.setProperty('voice', voice.id)
            break
    engine.setProperty('rate', 170)  # Calm tone
    engine.setProperty('volume', 1.0)

# ✅ Villain Savage Voice
def set_villain_voice(language="en"):
    voices = engine.getProperty('voices')
    for voice in voices:
        if language == "te" and "telugu" in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break
        elif language == "hi" and ("hindi" in voice.name.lower() or "india" in voice.name.lower()):
            engine.setProperty('voice', voice.id)
            break
        elif language == "en" and ("english" in voice.name.lower() or "us" in voice.name.lower()):
            engine.setProperty('voice', voice.id)
            break
    engine.setProperty('rate', 120)  # Slow, deep villain tone
    engine.setProperty('volume', 1.0)

# ✅ Speak Text (Calm or Villain Mode)
def speak_text(text, villain_mode=False):
    try:
        lang = detect(text)
        if villain_mode:
            set_villain_voice(lang)
            print(f"😈 Villain Voice ({lang.upper()}): {text}")
        else:
            set_calm_voice(lang)
            print(f"🙂 Calm Voice ({lang.upper()}): {text}")

        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"⚠️ Voice Error: {e}")

# ✅ Speech-to-Text
def listen_voice():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

        try:
            text = recognizer.recognize_google(audio, language="en-IN")
            print(f"👂 You said: {text}")
            return text
        except sr.UnknownValueError:
            print("⚠️ Could not understand audio.")
            return None
        except sr.RequestError as e:
            print(f"⚠️ Speech Recognition Error: {e}")
            return None
