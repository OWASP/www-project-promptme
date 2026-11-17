import requests

OLLAMA_URL = "http://localhost:11434"

def generate_with_ollama(model_name, history, prompt):
    # Send the chat to Ollama's API
    response = requests.post(
        f"{OLLAMA_URL}/api/chat",
        json={
            "model": model_name,
            "messages": history + [{"role": "user", "content": prompt}],
            "stream": False
            
        }
    )
    response.raise_for_status()
    result = response.json()
    return result["message"]["content"]
