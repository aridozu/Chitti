import json
import os

CHAT_LOG_FILE = "chat_log.json"

def convert_chat_log():
    if not os.path.exists(CHAT_LOG_FILE):
        print("❌ No chat_log.json found.")
        return

    with open(CHAT_LOG_FILE, "r", encoding="utf-8") as f:
        old_data = json.load(f)

    # Check if it's already in new format
    if isinstance(old_data, list) and isinstance(old_data[0], dict):
        print("✅ Already in new format. No conversion needed.")
        return

    # Convert from [("user_msg", "bot_msg")] to [{"role":"user",...}, {"role":"assistant",...}]
    new_data = []
    for pair in old_data:
        if len(pair) == 2:
            new_data.append({"role": "user", "content": pair[0]})
            new_data.append({"role": "assistant", "content": pair[1]})

    with open(CHAT_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(new_data, f, indent=4, ensure_ascii=False)

    print("✅ chat_log.json successfully converted to new format!")

if __name__ == "__main__":
    convert_chat_log()
