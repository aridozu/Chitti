import os
from dotenv import load_dotenv

load_dotenv()  # ✅ Loads variables from .env

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("❌ GROQ_API_KEY is missing. Check your .env file.")
else:
    print("✅ GROQ_API_KEY loaded successfully.")


