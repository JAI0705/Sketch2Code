import os
import requests

headers = {
    "Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
    "Content-Type": "application/json",
}

body = {
    "model": "mistralai/mixtral-8x7b-instruct",
    "messages": [
        {"role": "user", "content": "Say hello in HTML"}
    ]
}

res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body)
print(res.status_code)
print(res.json())
