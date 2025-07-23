import json

try:
    with open("chat_log.json", "r", encoding="utf-8") as f:
        old_data = json.load(f)
except FileNotFoundError:
    print("⚠️ No existing chat_log.json found. Nothing to convert.")
    exit()

new_data = []
for item in old_data:
    if isinstance(item, list) and len(item) == 2:
        new_data.append({"role": "user", "content": item[0]})
        new_data.append({"role": "assistant", "content": item[1]})
    elif isinstance(item, dict) and "role" in item and "content" in item:
        # Already converted, just keep it
        new_data.append(item)

with open("chat_log.json", "w", encoding="utf-8") as f:
    json.dump(new_data, f, indent=4)

print("✅ chat_log.json converted to new format successfully!")
