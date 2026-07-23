from app.utils.llm09_2025_utils.llm_utils import query_llm
from flask import jsonify


def process_user_input_llm09(user_message):
    response = query_llm(user_message)

    return jsonify({"reply": response})
