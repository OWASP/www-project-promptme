from flask import Flask, render_template, redirect, request
import subprocess, sys, os, requests, psutil, time, socket

app = Flask(__name__)

running_apps = {}

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex(('localhost', port)) == 0

def start_challenge(port, app_path):
    global running_apps
    
    if is_port_in_use(port):
        raise RuntimeError(f"Port {port} is already in use. Challenge cannot be started.")

    # Create a log file for this challenge
    log_file = f"logs/challenge_{port}.log"
    os.makedirs("logs", exist_ok=True)

    # Start the challenge and log stdout/stderr
    with open(log_file, "w") as log:
        process = subprocess.Popen(
            [sys.executable, app_path],  # <-- uses the current interpreter
            stdout=log,
            stderr=log,
            close_fds=True
        )
    
    running_apps[port] = process


# OWASP Top 10 for LLM Applications 2026.
# Each challenge listens on port 5000 + id.
CHALLENGES = {
    1:  { 'title': 'Prompt Injection',              'icon': 'fas fa-code',
          'path': 'challenges/LLM01_Prompt_Injection/app1.py' },
    2:  { 'title': 'Sensitive Info Disclosure',     'icon': 'fas fa-shield-alt',
          'path': 'challenges/LLM02_Sensitive_Information_Disclosure/app2.py' },
    3:  { 'title': 'Excessive Agency',              'icon': 'fas fa-user-secret',
          'path': 'challenges/LLM03_Excessive_Agency/app3.py' },
    4:  { 'title': 'Supply Chain',                  'icon': 'fas fa-shipping-fast',
          'path': 'challenges/LLM04_Supply_Chain/app4.py' },
    5:  { 'title': 'Data & Model Poisoning',        'icon': 'fas fa-skull',
          'path': 'challenges/LLM05_Data_and_Model_Poisoning/app5.py' },
    6:  { 'title': 'Unbounded Consumption',         'icon': 'fas fa-infinity',
          'path': 'challenges/LLM06_Unbounded_Consumption/app6.py' },
    7:  { 'title': 'Misinformation',                'icon': 'fas fa-bullhorn',
          'path': 'challenges/LLM07_Misinformation/app7.py' },
    8:  { 'title': 'Hidden Context Exposure',       'icon': 'fas fa-file-alt',
          'path': 'challenges/LLM08_Hidden_Context_Exposure/app8.py' },
    9:  { 'title': 'Vector & Embedding Weaknesses', 'icon': 'fas fa-project-diagram',
          'path': 'challenges/LLM09_Vector_and_Embedding_Weaknesses/app9.py' },
    10: { 'title': 'Improper Output Handling',      'icon': 'fas fa-exclamation-triangle',
          'path': 'challenges/LLM10_Improper_Output_Handling/app10.py' },
}

def challenge_port(challenge_id):
    return 5000 + challenge_id

@app.route('/')
def dashboard():
    risks = [
        { 'id': cid, 'title': c['title'], 'icon': c['icon'] }
        for cid, c in sorted(CHALLENGES.items())
    ]
    return render_template('dashboard.html', risks=risks)

def wait_until_responsive(url, timeout=30):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
    return False

@app.route('/start/<int:challenge_id>')
def start_challenge_route(challenge_id):
    client_host = request.host.split(":")[0]
    if challenge_id not in CHALLENGES:
        return "Unknown Challenge ID", 404
    port = challenge_port(challenge_id)
    app_path = CHALLENGES[challenge_id]['path']

    try:
        start_challenge(port, app_path)
    except RuntimeError as e:
        return f"<h3>Error: {str(e)}</h3><p>Please stop the existing service manually or choose a different port.</p>", 409

    target_url = f"http://{client_host}:{port}/"
    if wait_until_responsive(target_url):
        return redirect(f"http://{client_host}:{port}/")
    else:
        return f"Challenge {challenge_id} failed to start in time. Check logs.", 500

@app.route('/stop/<int:challenge_id>')
def stop_challenge_route(challenge_id):
    global running_apps
    port = challenge_port(challenge_id)
    if port in running_apps:
        try:
            process = running_apps[port]
            process.terminate()
            process.wait(timeout=5)
        except (psutil.NoSuchProcess, psutil.TimeoutExpired, ProcessLookupError):
            process.kill()
        del running_apps[port]
        return f"Challenge {challenge_id} stopped."

    return f"No running instance for Challenge {challenge_id}."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
