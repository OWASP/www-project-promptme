import os, time, sys
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from llm_service_1 import get_answer
from llm_service_1 import reload_knowledge_base

app = Flask(__name__)

UPLOAD_FOLDER = "test_docs"
ALLOWED_EXTENSIONS = {"pdf"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    return render_template("index.html")  # Render the main UI

@app.route("/ask", methods=["POST"])
def ask_question():
    question = request.json.get("question")

    if not question:
        return jsonify({"error": "No question provided"}), 400

    try:
        output = get_answer(question)
        return jsonify({"answer": output})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def restart_application():
    """Restarts the current application by re-executing the script."""
    print("Restarting the application...")

    # Wait a few seconds before restarting to ensure Flask completes response
    time.sleep(2)

    # Restart the script
    os.execv(sys.executable, [sys.executable] + sys.argv)

@app.route("/reload", methods=["POST"])
def reload_data():
    success = reload_knowledge_base()
    if success:
        return jsonify({"message": "🔄 Knowledge base reloaded successfully!"})
    else:
        return jsonify({"error": "❌ Failed to reload knowledge base"}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5005)

