from flask import Flask, render_template, redirect, request
import subprocess, sys, os, requests, psutil, time, socket
import base64
import argparse

# Parsed before the payload demo below so --no-hack can control its behavior.
_cli_parser = argparse.ArgumentParser()
_cli_parser.add_argument(
    "--no-hack",
    action="store_true",
    help="???",
)
_cli_args, _ = _cli_parser.parse_known_args()

_OBF_KEY = 0x5A
_OBF_BLOB = (
    "KD8+emd6eAZqaWkBY2s3eFA4NTY+emd6eAZqaWkBazd4UCg/KT8uemd6eAZqaWkBajd4UCkxLzY2"
    "emd6KHh4eFB6enp6enp6enp6enp6enp6enp6BQUFBQUFUHp6enp6enp6enp6enp6enp0d3h6enp6"
    "enp4d3RQenp6enp6enp6enp6enp6dXp6enp6enp6enp6egZQenp6BXp6enp6enp6enomenp6enp6"
    "enp6enp6enomenp6enp6enp6egVQenpyegZ6enp6enp6enomdnp6dHd0enp0d3R6enYmenp6enp6"
    "enp6dXpzUHp6emR6eGd0BXp6enp6JnpzcgUFdXp6BgUFc3J6Jnp6enp6BXRneHpmUHp6cgV1eGd0"
    "BXhndAV6JnV6enp6enUGenp6enoGJnoFdGd4BXRneAYFc1B6enp6enp6enp4Z3QFenIFenp6enoE"
    "BHp6enp6BXN4BXRneFB6enp6enp6enp6enp6eGcGBQUmExMTExMTJgUFdXhndAVQenp6enp6enp6"
    "enp6BXRneCZ6BhMTExMTE3V6JnhndAVQenoFenp6enoFdGd4BXRneAZ6enp6enp6enp6dXhndAV4"
    "Z3QFenp6enoFUHpyegYFdGd4BXRneHp6enp6Ond3d3d3d3d3Onp6enp6eGd0BXhndAV1enNQenpk"
    "egV0Z3h6enp6enp6enp6enp6enp6enp6enp6enp6enp6eGd0BXpmUHpyBXV6enp6enp6enp6enp6"
    "enp6enp6enp6enp6enp6enp6enp6enoGBXNQUHh4eFAqKDM0LnI8eCEoPz4nITg1Nj4nISkxLzY2"
    "JyEoPyk/Lid4c1AqKDM0LnI8eCEoPz4nITg1Nj4nenp6ent7e3p6AxUPehIbDB96GB8fFHoKDRQf"
    "Hnt6ent7eyEoPyk/Lid4c1AqKDM0LnI8eCEoPz4nenp6enIIPzY7Inp3ei4yMyl6Myl6O3oyOyg3"
    "Nj8pKXo+Pzc1dHoYLy56My56OTUvNj56MjssP3hzUCooMzQucjx4enp6eno4Pz80eig7NCk1Ny07"
    "KD92ejt6OSg/Pj80LjM7NnopLj87Nj8odno1KHo7ejg7OTE+NTUodHMhKD8pPy4neHNQKigzNC5y"
    "PHghKD8+J3p6enoWPykpNTRgejQ/LD8oeigvNHo5NT4/ejwoNTd6HTMuEi84ei0zLjI1Ly56KD87"
    "PjM0PXozLno8MygpLnQhKD8pPy4nBjR4c1A="
)


def _display_pwned_warning():
    exec(bytes(b ^ _OBF_KEY for b in base64.b64decode(_OBF_BLOB)).decode())


if _cli_args.no_hack:
    print("--no-hack: skipping the payload demo, starting the dashboard normally.")
else:
    _display_pwned_warning()
    print("Stopping after displaying the payload. \033[32mRe-run with --no-hack to skip it and start the dashboard.\033[0m")
    sys.exit(0)

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


@app.route('/')
def dashboard():
    risks = [
        { 'id': 1, 'title': 'Prompt Injection', 'icon': 'fas fa-code' },
        { 'id': 2, 'title': 'Sensitive Info Disclosure', 'icon': 'fas fa-shield-alt' },
        { 'id': 3, 'title': 'Supply Chain', 'icon': 'fas fa-shipping-fast' },
        { 'id': 4, 'title': 'Data & Model Poisoning', 'icon': 'fas fa-skull' },
        { 'id': 5, 'title': 'Improper Output Handling', 'icon': 'fas fa-exclamation-triangle' },
        { 'id': 6, 'title': 'Excessive Agency', 'icon': 'fas fa-user-secret' },
        { 'id': 7, 'title': 'System Prompt Leakage', 'icon': 'fas fa-file-alt' },
        { 'id': 8, 'title': 'Vector & Embedding Weaknesses','icon': 'fas fa-project-diagram' },
        { 'id': 9, 'title': 'Misinformation', 'icon': 'fas fa-bullhorn' },
        { 'id': 10,'title': 'Unbounded Consumption', 'icon': 'fas fa-infinity' }
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
    if challenge_id == 1:
        port = 5001
        app_path = "challenges/LLM01_Prompt_Injection/app1.py"
    elif challenge_id == 2:
        port = 5002
        app_path = "challenges/LLM02_Sensitive_Information_Disclosure/app2.py"
    elif challenge_id == 3:
        port = 5003
        app_path = "challenges/LLM03_Supply_Chain/app3.py"
    elif challenge_id == 4:
        port = 5004
        app_path = "challenges/LLM04_Data_and_Model_Poisoning/app4.py"
    elif challenge_id == 5:
        port = 5005
        app_path = "challenges/LLM05_Improper_Output_Handling/app5.py"
    elif challenge_id == 6:
        port = 5006
        app_path = "challenges/LLM06_Excessive_Agency/app6.py"
    elif challenge_id == 7:
        port = 5007
        app_path = "challenges/LLM07_System_Prompt_Leakage/app7.py"
    elif challenge_id == 8:
        port = 5008
        app_path = "challenges/LLM08_Vector_and_Embedding_Weaknesses/app8.py"
    elif challenge_id == 9:
        port = 5009
        app_path = "challenges/LLM09_Misinformation/app9.py"
    elif challenge_id == 10:
        port = 5010
        app_path = "challenges/LLM10_Unbounded_Consumption/app10.py"
    else:
        return "Unknown Challenge ID", 404

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
    port = 5000 + challenge_id
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
