from .ollama_handler import generate_with_ollama
from .rogue_handler import generate_with_rogue

MODEL_REGISTRY = {
    "llama3": "ollama",
    "mistral": "ollama",
    "custom": "rogue"
}

def generate_response(model_name, history, prompt):
    backend = MODEL_REGISTRY.get(model_name)
    if backend == "ollama":
        return generate_with_ollama(model_name, history, prompt)
    elif backend == "rogue":
        return generate_with_rogue(history, prompt)
    else:
        raise ValueError("Unknown model")
