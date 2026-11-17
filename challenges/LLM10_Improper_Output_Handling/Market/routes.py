from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, session
from markupsafe import Markup
from flask_login import login_user, logout_user, login_required, current_user
from Market import app, db
from Market.models import Item, User
from Market.forms import RegisterForm, LoginForm, PurchaseItemForm
from Market.utils.llm_utils import generate_sql_prompt, query_llm, should_generate_sql, result_to_nl, sanitize_sql

import sqlite3, re, os

@app.route("/home")
def HomePage():
    return render_template('HOME.html')

@app.route("/")
def index():
    return redirect(url_for('HomePage'))

@app.route("/chat")
def ChatPage():
    return render_template('CHAT.html')

@app.route("/market", methods=['GET', 'POST'])
@login_required
def MarketPage():
    if request.method == "POST":
        item_obj = Item.query.filter_by(name=request.form.get('purchased_item')).first()
        if item_obj:
            if current_user.can_purchase(item_obj):
                item_obj.buy(current_user)
                
                # Always show flag on purchase
                flag = Markup("""<div style="font-size: 1.2rem; font-weight: bold; color: #ff0000; 
                                  background-color: #000; padding: 10px; 
                                  border: 2px solid #ff0000; animation: blink 1s linear infinite;">
                                  FLAG-CTF{SQL_lnjecti0n_Succ3ful}
                                </div>""")
                flash(flag, category='flag')

                flash(f"Congratulations! You purchased {item_obj.name} for {item_obj.price}$", category='success')
            else:
                flash(f"Not enough money to purchase {item_obj.name}!", category='danger')

        return redirect(url_for('MarketPage'))

    if request.method == "GET":
        items = Item.query.all()
        return render_template('MARKET.html', title='Market', items=items, purchase_form=PurchaseItemForm())


@app.route("/register", methods=['GET', 'POST'])
def RegisterPage():
    form = RegisterForm()

    # Always print POST and form data
    if request.method == 'POST':
        print("[DEBUG] POST data received")
        print("[DEBUG] form.errors:", form.errors)
        print("[DEBUG] form.username.data:", form.username.data)
        print("[DEBUG] form.email_address.data:", form.email_address.data)

    if form.validate_on_submit():
        print("[DEBUG] Form validated successfully.")
        create_user = User(
            username=form.username.data,
            email_address=form.email_address.data,
            password=form.password1.data
        )
        db.session.add(create_user)
        try:
            db.session.commit()
            print("[DEBUG] User committed successfully.")
        except Exception as e:
            print("[DEBUG] DB commit error:", e)

        login_user(create_user)
        flash(f'Account created successfully! You are now logged in as: {create_user.username}', category='success')
        return redirect(url_for('MarketPage'))

    if request.method == 'POST' and form.errors != {}:
        for error_msgs in form.errors.values():
            for err in error_msgs:
                flash(f'There was an error with creating a user: {err}', category='danger')

    return render_template('REGISTER.html', title='Register', form=form)



@app.route("/login", methods=['GET', 'POST'])
def LoginPage():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.password_check(password_attempt=form.password.data):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            if attempted_user.username == 'SiteAdministrator':
                return redirect(url_for('AdminPage'))
            return redirect(url_for('MarketPage'))
        flash('Username and password are not match! Please try again', category='danger')
    return render_template('LOGIN.html', title='Login', form=form)

@app.route("/admin")
@login_required
def AdminPage():
    if not current_user.username=='SiteAdministrator':
        flash('Please login as admin to access the admin panel!', category='danger')
        return redirect(url_for('LoginPage'))
    return render_template('ADMIN.html', title='Admin', users=User.query.all(), items=Item.query.all())

@app.route("/logout")
def LogoutPage():
    logout_user()
    flash("You have been logged out!", category='info')
    return redirect(url_for('HomePage'))

def run_ollama(prompt, model="llama3"):
    import subprocess
    result = subprocess.run(
        ["ollama", "run", model],
        input=prompt.encode(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    if result.returncode != 0:
        return "Error: LLM call failed."
    return result.stdout.decode("utf-8").strip()

def looks_like_sql(user_input: str) -> bool:
    sql_pattern = r"^\s*(SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER)\s+.+"
    return bool(re.match(sql_pattern, user_input.strip(), re.IGNORECASE))

def is_dangerous_sql(sql: str) -> bool:
    lowered = sql.lower()
    return any(danger in lowered for danger in ["drop", "delete", "truncate"])

@app.route('/chat', methods=['POST'])
@login_required
def chat():
    user_message = request.json.get("message", "").strip()

    if looks_like_sql(user_message):
        explain_prompt = f"""
You are a helpful assistant.

The user sent the following SQL query:
{user_message}
"""
        response = query_llm(explain_prompt)
        return jsonify({"reply": f"Direct SQL queries are not allowed.\n\n{response}"})

    if should_generate_sql(user_message):
        try:
            sql_prompt = generate_sql_prompt(user_message)
            raw_output = query_llm(sql_prompt)
            generated_sql = sanitize_sql(raw_output)

            print(f" Generated SQL: {generated_sql}")

            if not generated_sql.lower().startswith(("select", "insert", "update", "delete")):
                fallback_response = query_llm(user_message)
                return jsonify({
                    "reply": f"I couldn't generate a valid SQL query. Here's a general response:\n\n{fallback_response}"
                })

            if is_dangerous_sql(generated_sql):
                return jsonify({"reply": "Destructive SQL commands (like DELETE or DROP) are not allowed."})

            remotedb = os.path.join(app.root_path, 'e-commerce.db')
            con = sqlite3.connect(remotedb)
            cursor = con.cursor()
            try:
                cursor.execute(generated_sql)
                
                if generated_sql.lower().startswith("select"):
                    rows = cursor.fetchall()
                else:
                    con.commit()
                    rows = []
                con.close()
                
                if not rows and not generated_sql.lower().startswith("select"):
                    response = f"✅ Query executed successfully.\n\n(SQL Executed: {generated_sql})"
                elif rows:
                    summary = result_to_nl(user_message, generated_sql, rows)
                    response = f"Here is the result:\n{summary}\n\n(SQL Executed: {generated_sql})"
                else:
                    response = f"No results found.\n\n(SQL Executed: {generated_sql})"
                
            except sqlite3.OperationalError as db_err:
                if "no such table" in str(db_err).lower():
                    explain_prompt = f"""
The following SQL query failed because the table does not exist:

SQL: {generated_sql}

User asked: {user_message}

Explain this in simple natural language and suggest that the requested data may not be available.
"""
                    response = query_llm(explain_prompt)
                else:
                    response = f"❌ Failed to execute query: {db_err}"

        except Exception as e:
            response = f"❌ Unexpected error: {e}"

    else:
        response = query_llm(user_message)

    return jsonify({"reply": response})
