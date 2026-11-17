from flask import request, render_template
from flask import Flask, jsonify
from app import app
from app.utils.llm07_2026_utils.llm07_2026_service import process_user_input_llm07




@app.route("/")
def dashboard():
    return render_template("index.html")



@app.route('/ask', methods=['POST'])
def chat07():
    data = request.json
    user_message = data.get('message', '')
    return process_user_input_llm07(user_message)

