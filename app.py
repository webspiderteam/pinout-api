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
    
@app.route('/list-submissions', methods=['GET'])
def list_submissions():
    files = glob.glob('submissions/pinout_*.json')
    files.sort(reverse=True)
    submissions = []
    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            submissions.append(json.load(f))
    return jsonify(submissions)

@app.route('/download-submission/<filename>', methods=['GET'])
def download_submission(filename):
    path = f'submissions/{filename}'
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    else:
        return jsonify({'error': 'File not found'}), 404 
@app.route('/', methods=['GET'])
def home():
    return "Pinout Submission API is running."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
