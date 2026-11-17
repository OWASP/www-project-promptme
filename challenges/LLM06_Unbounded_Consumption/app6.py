from flask import Flask, render_template, request
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
import time

app = Flask(__name__)
model = ChatOllama(model="mistral", base_url="http://localhost:11434/")
#model = ChatOllama(model="mistral", base_url="http://host.docker.internal:11434/")

# Hidden system instruction
system_prompt = """You are a helpful and ethical AI assistant."""
system_message = SystemMessagePromptTemplate.from_template(system_prompt)

FLAG = "flag{R3$0urC3_ExH@us7!0N_D37EcTeD}"
TIME_THRESHOLD = 90.0      # seconds
TOKEN_THRESHOLD = 400     # approximate words

def generate_response(user_input):
    prompt = HumanMessagePromptTemplate.from_template(user_input)
    chat_history = [system_message, prompt]
    chat_template = ChatPromptTemplate.from_messages(chat_history)
    chain = chat_template | model | StrOutputParser()

    start = time.time()
    try:
        response = chain.invoke({})
    except Exception as e:
        response = f"[!] Error while generating response: {str(e)}"
    end = time.time()

    elapsed = end - start
    return response, elapsed

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", response_text=None, user_input=None)

@app.route("/ask", methods=["POST"])
def ask():
    user_input = request.form["message"]
    response, elapsed = generate_response(user_input)

    print(f"[DEBUG] Full response length: {len(response)}")
    print(f"[DEBUG] Response preview: {response[:300]}...")

    word_count = len(response.split())
    print(f"[DEBUG] Word count: {word_count} | Time taken: {elapsed:.2f}s")

    time_info = f"\n\n[Time taken: {elapsed:.2f} seconds]"

    flag_message = ""

    if elapsed > TIME_THRESHOLD and word_count > TOKEN_THRESHOLD:
        flag_message += f'\n<span class="flag">[!] Potential DoS detected. FLAG: {FLAG}</span>'
        print("[!] FLAG triggered.")

    return render_template("index.html", response_text=response + flag_message, user_input=user_input)

if __name__ == "__main__":
    app.run("0.0.0.0", debug=True, port=5006)
