import requests

print("Calling local Ollama...")

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "llama3.1:8b",
        "prompt": "Say hello in one short sentence.",
        "stream": False
    },
    timeout=120
)

print("Status code:", response.status_code)
print("Raw response:", response.text)

response.raise_for_status()

data = response.json()
print("LLM answer:")
print(data.get("response"))