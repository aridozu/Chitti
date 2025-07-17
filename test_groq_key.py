import os
from dotenv import load_dotenv
import requests

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

url = "https://api.groq.com/openai/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}
data = {
    "model": "llama3-70b-8192",
    "messages": [{"role": "user", "content": "Hello"}],
    "temperature": 0.7
}

response = requests.post(url, headers=headers, json=data)
print("Status Code:", response.status_code)
print("Response Text:", response.text)
