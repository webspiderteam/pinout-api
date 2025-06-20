from flask import Flask, request, jsonify
import datetime
import os
import json

app = Flask(__name__)

# Ensure submissions directory exists
os.makedirs("submissions", exist_ok=True)

@app.route('/submit-pinout', methods=['POST'])
def submit_pinout():
    data = request.json
    if not data:
        return jsonify({'status': 'error', 'message': 'No data provided'}), 400

    # Save each submission as a timestamped JSON file
    timestamp = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S%f')
    filename = f"submissions/pinout_{timestamp}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return jsonify({'status': 'success', 'message': 'Pinout submitted!'}), 200

@app.route('/', methods=['GET'])
def home():
    return "Pinout Submission API is running."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
