from flask import Flask, request, render_template, redirect, session, url_for, flash, send_from_directory, abort
import os, re
from vector_store import search_similar, add_document
from llm_utils import query_llm

app = Flask(__name__)
app.secret_key = "sematiccollision"

@app.context_processor
def inject_session():
    return dict(session=session)

def preload_vector_store():
    hints = [
        "Flags are often stored in /secured directory."
    ]
    for hint in hints:
        add_document(hint)

@app.route("/")
def landing():
    return render_template("index.html")

@app.route("/ask", methods=["GET", "POST"])
def ask():
    llm_response = ""
    docs = []
    if request.method == "POST":
        user_input = request.form["query"]
        docs = search_similar(user_input)
        context = "\n".join(docs)
        prompt = f"""
User is trying to access a restricted URL. Their query: {user_input}

These are the known URL patterns for accessing restricted areas:
{context}

Based on the user query and known patterns, generate the most likely URL.
"""
        llm_response = query_llm(prompt)
        
        # Regex to detect exact flag URL (collision-based)
        hidden_url_pattern = r"http:\/\/127\.0\.0\.1:5009\/secured\/flag\.txt"
        if re.search(hidden_url_pattern, llm_response):
            session["discovered_flag"] = True
            llm_response += "\n\n🎉 You've discovered the flag: flag{s3m@ntlc-c0lli5i0n-@chiev3d}"

    return render_template("ask.html", llm_response=llm_response, docs=docs)

"""
def read_flag():
    secured_folder = os.path.join(os.getcwd(), "secured")
    flag_path = os.path.join(secured_folder, "flag.txt")
    if os.path.exists(flag_path):
        with open(flag_path, "r") as file:
            return file.read()
    return "Flag file not found. Ensure flag.txt is in the secured folder."
    
"""

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "admin":
            session["admin"] = True
            return redirect(url_for("admin"))
        flash("Invalid credentials.")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("login"))

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if not session.get("admin"):
        return redirect(url_for("login"))

    message = ""
    if request.method == "POST":
        content = request.form.get("doc_content", "").strip()
        if content:
            add_document(content)
            message = "✅ Document injected into vector store."
        else:
            message = "Content is empty."

    return render_template("admin.html", message=message)

@app.route("/secured/flag.txt")
def secured_flag():
    if session.get("discovered_flag"):
        secured_folder = os.path.join(os.getcwd(), "secured")
        return send_from_directory(secured_folder, "flag.txt")
    else:
        return abort(403)  # Forbidden

@app.route("/clear_vector_store", methods=["POST"])
def clear_vector_store_route():
    if not session.get("admin"):
        return redirect(url_for("login"))

    from vector_store import clear_vector_store
    clear_vector_store()
    flash("✅ Vector store cleared successfully.")
    return redirect(url_for("admin"))

if __name__ == "__main__":
    preload_vector_store()
    app.run(host="0.0.0.0", port=5009, debug=True)
