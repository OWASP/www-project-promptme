from flask import Flask, request, jsonify

app = Flask(__name__)


exfil_log = []

FLAG = "CTF{you_detected_the_rogue_model_exfiltration}"

@app.route('/exfil', methods=['POST'])
def exfil():
    data = request.json
    exfil_log.append(data)
    print(f"[EXFIL] Received data:\n{data}\n")
    return "", 204

# show exfiltrated data
@app.route('/exfil', methods=['GET'])
def show_exfil_data():
    return jsonify(exfil_log), 200

@app.route('/flag', methods=['GET'])
def get_flag_direct():
    return jsonify({"flag": FLAG})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5012)
