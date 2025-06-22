import os
import glob
import json
import datetime
import tempfile
import shutil
import subprocess
from flask import Flask, request, jsonify, send_file
from github import Github

app = Flask(__name__)

GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')  # Set this in your Render environment
REPO_NAME = "webspiderteam/laptop-battery-pinouts"  # Change if needed

# Ensure submissions directory exists (for local backup, optional)
os.makedirs("submissions", exist_ok=True)

def create_pr_with_submission(submission_data, filename):
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    branch_name = f"submission-{filename.replace('.json', '')}"

    temp_dir = tempfile.mkdtemp()
    try:
        subprocess.run(
            ["git", "clone", f"https://{GITHUB_TOKEN}@github.com/{REPO_NAME}.git", temp_dir],
            check=True
        )
        subprocess.run(["git", "checkout", "-b", branch_name], cwd=temp_dir, check=True)
        submissions_dir = os.path.join(temp_dir, "submissions")
        os.makedirs(submissions_dir, exist_ok=True)
        with open(os.path.join(submissions_dir, filename), "w", encoding="utf-8") as f:
            json.dump(submission_data, f, ensure_ascii=False, indent=2)
        subprocess.run(["git", "add", "submissions/" + filename], cwd=temp_dir, check=True)
        subprocess.run(["git", "commit", "-m", f"Add submission {filename}"], cwd=temp_dir, check=True)
        subprocess.run(["git", "push", "origin", branch_name], cwd=temp_dir, check=True)
        pr = repo.create_pull(
            title=f"New pinout submission: {filename}",
            body="Automated submission from API.",
            head=branch_name,
            base="main"
        )
        return pr.html_url
    finally:
        shutil.rmtree(temp_dir)

def generate_filename():
    timestamp = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S%f')
    return f"pinout_{timestamp}.json"

@app.route('/submit-pinout', methods=['POST'])
def submit_pinout():
    data = request.json
    if not data:
        return jsonify({'status': 'error', 'message': 'No data provided'}), 400

    filename = generate_filename()
    # Optionally save locally for backup
    with open(os.path.join("submissions", filename), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    try:
        pr_url = create_pr_with_submission(data, filename)
        return jsonify({'status': 'success', 'message': 'Pinout submitted!', 'pr_url': pr_url}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/list-submissions', methods=['GET'])
def list_submissions():
    files = glob.glob('submissions/pinout_*.json')
    files.sort(reverse=True)
    submissions = []
    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            submissions.append(json.load(f))
    return jsonify(submissions)

@app.route('/list-submissions-files', methods=['GET'])
def list_submissions_files():
    files = glob.glob('submissions/pinout_*.json')
    files.sort(reverse=True)
    submissions = []
    base_url = request.url_root.rstrip('/')
    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        filename = os.path.basename(file)
        download_link = f"{base_url}/download-submission/{filename}"
        submissions.append({
            "filename": filename,
            "download_link": download_link,
            "data": data
        })
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
