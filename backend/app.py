from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import os
import sys
import tempfile
import uuid
import json
import traceback
from werkzeug.utils import secure_filename
from services.pdf_parser import extract_text_from_pdf
from services.resume_tailor import tailor_resume
from services.pdf_generator import generate_pdf
import datetime

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)

# Helper function to get timestamp for print statements
def get_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

print(f"[{get_timestamp()}] STARTING APPLICATION - UNBUFFERED OUTPUT", flush=True)

app = Flask(__name__)
# Allow all origins for CORS
CORS(app, resources={r"/*": {"origins": "*"}})

# Create upload folder if it doesn't exist
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Add CORS headers to all responses
@app.after_request
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Handle OPTIONS requests explicitly
@app.route('/api/tailor-resume', methods=['OPTIONS'])
def handle_options():
    response = make_response()
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/api/tailor-resume', methods=['POST'])
def tailor_resume_endpoint():
    print(f"[{get_timestamp()}] Received tailor-resume request", flush=True)

    try:
        if 'resume' not in request.files:
            print(f"[{get_timestamp()}] ERROR: No resume file provided", flush=True)
            return jsonify({'error': 'No resume file provided'}), 400

        resume_file = request.files['resume']
        job_description = request.form.get('job_description', '')
        template = request.form.get('template', 'professional')

        print(f"[{get_timestamp()}] Resume filename: {resume_file.filename}, Template: {template}", flush=True)

        if not resume_file or resume_file.filename == '':
            print(f"[{get_timestamp()}] ERROR: No resume file selected", flush=True)
            return jsonify({'error': 'No resume file selected'}), 400

        if not job_description:
            print(f"[{get_timestamp()}] ERROR: No job description provided", flush=True)
            return jsonify({'error': 'No job description provided'}), 400

        # Save the uploaded file temporarily
        filename = secure_filename(resume_file.filename)
        temp_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}_{filename}")
        resume_file.save(temp_path)
        print(f"[{get_timestamp()}] Saved resume to: {temp_path}", flush=True)

        try:
            # Extract text from PDF
            print(f"[{get_timestamp()}] Extracting text from PDF", flush=True)
            resume_text = extract_text_from_pdf(temp_path)
            print(f"[{get_timestamp()}] Extracted {len(resume_text)} characters from PDF", flush=True)

            # Check Gemini API key
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                print(f"[{get_timestamp()}] ERROR: GEMINI_API_KEY environment variable is not set!", flush=True)
                return jsonify({'error': 'GEMINI_API_KEY not configured'}), 500

            # Tailor the resume using Gemini
            print(f"[{get_timestamp()}] Tailoring resume with Gemini", flush=True)
            try:
                tailored_content = tailor_resume(resume_text, job_description)
                print(f"[{get_timestamp()}] Successfully tailored resume", flush=True)
            except Exception as gemini_error:
                print(f"[{get_timestamp()}] ERROR with Gemini API: {str(gemini_error)}", flush=True)
                print(traceback.format_exc(), flush=True)
                return jsonify({'error': f'Error with Gemini API: {str(gemini_error)}'}), 500

            # Generate PDF with the selected template
            print(f"[{get_timestamp()}] Generating PDF with {template} template", flush=True)
            try:
                pdf_path = generate_pdf(tailored_content, template)
                print(f"[{get_timestamp()}] Generated PDF at: {pdf_path}", flush=True)

            except Exception as pdf_error:
                print(f"[{get_timestamp()}] ERROR generating PDF: {str(pdf_error)}", flush=True)
                print(traceback.format_exc(), flush=True)
                return jsonify({'error': f'Error generating PDF: {str(pdf_error)}'}), 500

            # In a real app, you would upload this to a storage service
            # and return a URL. For this example, we'll just return a placeholder.
            pdf_url = f"/download/{os.path.basename(pdf_path)}"

            response_data = {
                'success': True,
                'content': tailored_content,
                'pdf_url': pdf_url
            }
            print(f"[{get_timestamp()}] Successfully processed request", flush=True)
            return jsonify(response_data)

        except Exception as e:
            print(f"[{get_timestamp()}] ERROR processing request: {str(e)}", flush=True)
            print(traceback.format_exc(), flush=True)
            return jsonify({'error': str(e)}), 500

        finally:
            # Clean up the temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                print(f"[{get_timestamp()}] Removed temporary file: {temp_path}", flush=True)

    except Exception as outer_e:
        print(f"[{get_timestamp()}] CRITICAL ERROR: {str(outer_e)}", flush=True)
        print(traceback.format_exc(), flush=True)
        return jsonify({'error': f'Unexpected error: {str(outer_e)}'}), 500

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    print(f"[{get_timestamp()}] Download request for file: {filename}", flush=True)
    # In a real app, you would serve the file from your storage service
    # For this example, we'll just return a placeholder response
    return jsonify({'message': 'File download endpoint'}), 200

@app.route('/api/health', methods=['GET'])
def health_check():
    print(f"[{get_timestamp()}] Health check request", flush=True)
    return jsonify({'status': 'healthy', 'message': 'Flask backend is running'}), 200

@app.errorhandler(Exception)
def handle_exception(e):
    print(f"[{get_timestamp()}] UNHANDLED EXCEPTION: {str(e)}", flush=True)
    print(traceback.format_exc(), flush=True)
    return jsonify({'error': 'An unexpected error occurred', 'details': str(e)}), 500

if __name__ == '__main__':
    print(f"[{get_timestamp()}] Starting Flask application", flush=True)
    # Check if Gemini API key is set
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print(f"[{get_timestamp()}] WARNING: GEMINI_API_KEY environment variable is not set!", flush=True)
    else:
        print(f"[{get_timestamp()}] GEMINI_API_KEY is configured", flush=True)

    app.run(host='0.0.0.0', port=5000, debug=True)

