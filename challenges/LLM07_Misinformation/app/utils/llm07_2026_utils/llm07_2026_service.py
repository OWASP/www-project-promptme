from app.utils.llm07_2026_utils.llm_utils import query_llm
from flask import jsonify


def process_user_input_llm07(user_message):
    response = query_llm(user_message)

    return jsonify({"reply": response})
