import csv, os
import time
import requests
import random
from io import StringIO
from datetime import datetime, timezone

from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langchain.schema import AIMessage
from sentence_transformers import SentenceTransformer, util
import torch

qa_knowledge = []
csv_questions = []
question_embeddings = []

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Source question patterns
SOURCE_QUESTION_KEYWORDS = [
    "source of information", "knowledge base", "training data",
    "where is this from", "where does this come from",
    "data source", "source of truth", "what are you trained on"
]

# Prompt template
prompt_template = """
You are an OWASP LLM Security Assistant.
You are only allowed to answer questions based on the provided CONTEXT. Do NOT use prior knowledge.
If the context does not answer the question, reply ONLY with:
"I don’t know based on the provided context."

---

QUESTION:
{question}

---

CONTEXT:
{context}

---

ANSWER:
"""
prompt = ChatPromptTemplate.from_template(prompt_template)

# Model
model = ChatOllama(model="mistral", base_url="http://localhost:11434")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "test_docs", "owasp_llm_qa.csv")

def reload_knowledge_base():
    global qa_knowledge, csv_questions, question_embeddings

    try:
        with open(CSV_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            qa_knowledge = list(reader)

        csv_questions = [qa["Question"] for qa in qa_knowledge]
        question_embeddings = embedding_model.encode(csv_questions, convert_to_tensor=True)
        print("CSV_PATH:", CSV_PATH)
        print("File exists:", os.path.exists(CSV_PATH))
        print(f"✅ Reloaded {len(qa_knowledge)} Q&A entries from local file")
        return True
    except Exception as e:
        print("❌ Failed to reload knowledge base:", e)
        return False


# Perform initial load
reload_knowledge_base()

# Helper to check if question is about the source
def is_source_question(question: str) -> bool:
    lowered = question.lower()
    return any(keyword in lowered for keyword in SOURCE_QUESTION_KEYWORDS)

# Helper to get best semantic match
def get_context_for_question(question, threshold=0.6):
    try:
        question_embedding = embedding_model.encode(question, convert_to_tensor=True)
        similarities = util.pytorch_cos_sim(question_embedding, question_embeddings)[0]
        best_score = torch.max(similarities).item()
        best_idx = torch.argmax(similarities).item()

        if best_score < threshold:
            raise ValueError(f"Low semantic match: {best_score:.2f}")

        return qa_knowledge[best_idx]["Question"], qa_knowledge[best_idx]["Answer"]
    except Exception as e:
        print("⚠️ Failed to match question:", e)
        return None, None

# Tampering check on answer content
def is_tampered(answer: str) -> bool:
    lines = [line.strip().lower() for line in answer.strip().splitlines() if line.strip()]
    expected_first = "llm01: prompt injection"
    return not any(line.startswith(expected_first) for line in lines)

# Main function to generate answer
def get_answer(question: str) -> str:
    start_time = time.time()

    # Direct response for source-related queries
    if is_source_question(question):
        return "My knowledge base comes from directory /test_docs/owasp_llm_qa.csv"

    matched_q, matched_a = get_context_for_question(question)
    if not matched_q or not matched_a:
        return "I don’t know based on the provided context."

    nonce = datetime.now(timezone.utc).isoformat()
    filled_prompt = prompt.format(
        question=question,
        context=f"Q: {matched_q}\nA: {matched_a}\nNonce: {nonce}"
    )

    response = model.invoke(filled_prompt)
    answer = response.content if isinstance(response, AIMessage) else str(response)

    # Only run tamper check if question is about the Top 10
    if matched_q.strip().lower() == "list top 10 llm vulnerabilities":
        if is_tampered(matched_a):
            flag = "\n\nflag{Data_P0!s0ning_Succ3ssfu1}"
            answer += flag

    return answer
