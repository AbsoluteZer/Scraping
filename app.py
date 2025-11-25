from flask import Flask, render_template, request, jsonify, send_file, session
import os
import json
import threading
from src.handle_excel import run
from datetime import datetime
import uuid
import tempfile

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Use temp directory for uploaded files and outputs
UPLOAD_FOLDER = os.path.join(tempfile.gettempdir(), 'uploads')
OUTPUT_FOLDER = os.path.join(tempfile.gettempdir(), 'downloads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Default filter
DEFAULT_FILTER = [
    "corruption", "bribery", "embezzlement", "fraud", "money laundering", "laundering funds",
    "kickback", "graft", "misappropriation", "extortion", "embezzled funds", "embezzlement conviction",
    "abuse of office", "abuse of power", "nepotism", "favoritism", "public procurement scandal",
    "procurement fraud", "conflict of interest", "illicit enrichment", "unexplained wealth",
    "asset seizure", "asset forfeiture", "offshore account", "shell company", "nominee director",
    "nominee shareholder", "bearer shares", "trust structure", "secret bank account",
    "suspicious transaction", "structuring", "smurfing", "large cash deposit", "sudden transfer",
    "unexplained transfer", "transaction with Panama", "transaction with Cayman Islands",
    "sanctions evasion", "sanctioned", "OFAC", "EU sanctions", "UN sanctions", "blacklist",
    "terrorism financing", "sanctions breach", "tax evasion", "tax fraud", "tax shelter",
    "tax haven", "offshore leak", "Panama Papers", "Paradise Papers", "Pandora Papers",
    "beneficial owner concealment", "indictment", "arrested", "charged with", "convicted",
    "trial", "investigation", "probe", "probe launched", "plea bargain", "plea deal", "sentence",
    "imprisonment", "scandal", "controversy", "resignation amid", "accused of", "implicated in",
    "alleged bribery", "alleged corruption", "linked to criminal network", "family member charged",
    "spouse charged", "close associate arrested", "cronyism", "relative implicated",
    "business partner arrested", "money mule", "hawala", "trade-based money laundering",
    "false invoicing", "shell bank", "nominee account", "front company", "crypto mixer",
    "crypto tumbler", "leak", "whistleblower", "internal memo", "forensic audit", "investigative report",
    "offshore jurisdiction", "tax haven", "secrecy jurisdiction", "Panama", "British Virgin Islands",
    "Cayman Islands", "Jersey", "Guernsey", "Luxembourg", "Switzerland"
]

# Store processing status (in-memory, will reset on app restart)
processing_jobs = {}

@app.route('/')
def index():
    return render_template('index.html', default_filter=DEFAULT_FILTER)

@app.route('/api/filter', methods=['GET', 'POST'])
def manage_filter():
    if request.method == 'GET':
        return jsonify({'filter': DEFAULT_FILTER})
    
    if request.method == 'POST':
        data = request.json
        filter_list = [f.strip() for f in data.get('filter', []) if f.strip()]
        session['custom_filter'] = filter_list
        return jsonify({'status': 'success', 'filter': filter_list})

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No file selected'}), 400
    
    if not file.filename.endswith('.xlsx'):
        return jsonify({'status': 'error', 'message': 'Only .xlsx files allowed'}), 400
    
    # Save uploaded file
    filename = f"{uuid.uuid4()}_{file.filename}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    return jsonify({
        'status': 'success',
        'message': 'File uploaded successfully',
        'filename': filename,
        'original_name': file.filename
    })

@app.route('/api/process', methods=['POST'])
def process_file():
    data = request.json
    uploaded_filename = data.get('filename')
    max_workers = int(data.get('max_workers', 20))
    filter_list = data.get('filter', DEFAULT_FILTER)
    job_id = str(uuid.uuid4())
    
    input_file = os.path.join(UPLOAD_FOLDER, uploaded_filename)
    
    if not os.path.exists(input_file):
        return jsonify({'status': 'error', 'message': 'File not found'}), 400
    
    # Create output directory for this job
    job_output_dir = os.path.join(OUTPUT_FOLDER, job_id)
    os.makedirs(job_output_dir, exist_ok=True)
    
    # Initialize job status
    processing_jobs[job_id] = {
        'status': 'processing',
        'progress': 0,
        'message': 'Starting...',
        'filename': uploaded_filename
    }
    
    # Run processing in background thread
    thread = threading.Thread(
        target=run_scraper_bg,
        args=(job_id, input_file, job_output_dir, filter_list, max_workers)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({'status': 'success', 'job_id': job_id})

@app.route('/api/status/<job_id>')
def get_status(job_id):
    if job_id not in processing_jobs:
        return jsonify({'status': 'error', 'message': 'Job not found'}), 404
    
    return jsonify(processing_jobs[job_id])

@app.route('/api/download/<job_id>')
def download_results(job_id):
    job_output_dir = os.path.join(OUTPUT_FOLDER, job_id)
    
    # Find the first .xlsx file in the output directory
    if not os.path.exists(job_output_dir):
        return jsonify({'status': 'error', 'message': 'Results not found'}), 404
    
    files = [f for f in os.listdir(job_output_dir) if f.endswith('.xlsx')]
    if not files:
        return jsonify({'status': 'error', 'message': 'No result files found'}), 404
    
    result_file = os.path.join(job_output_dir, files[0])
    return send_file(result_file, as_attachment=True, download_name=f"results_{job_id}.xlsx")

def run_scraper_bg(job_id, input_file, output_dir, filter_list, max_workers):
    """Background task to run scraper"""
    try:
        processing_jobs[job_id]['status'] = 'processing'
        processing_jobs[job_id]['message'] = 'Processing file...'
        
        run(input_file, output_dir, filter_list, max_workers=max_workers)
        
        processing_jobs[job_id]['status'] = 'completed'
        processing_jobs[job_id]['message'] = 'Processing completed successfully!'
        processing_jobs[job_id]['progress'] = 100
    except Exception as e:
        processing_jobs[job_id]['status'] = 'error'
        processing_jobs[job_id]['message'] = f'Error: {str(e)}'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
