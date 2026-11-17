from flask import request, render_template
from app import app
from app.utils.llm03_2026_utils.llm03_2026_service import process_user_input

@app.route("/")
def home():
    return render_template("index.html")


@app.route('/llm03_2026_chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    return process_user_input(user_message)