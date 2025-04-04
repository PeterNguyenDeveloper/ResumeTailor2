from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import os
import tempfile
import uuid
import json
import logging
import traceback
from werkzeug.utils import secure_filename
from services.pdf_parser import extract_text_from_pdf
from services.resume_tailor import tailor_resume
from services.pdf_generator import generate_pdf

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
    if 'resume' not in request.files:
        return jsonify({'error': 'No resume file provided'}), 400

    resume_file = request.files['resume']
    job_description = request.form.get('job_description', '')
    template = request.form.get('template', 'professional')

    if not resume_file or resume_file.filename == '':
        return jsonify({'error': 'No resume file selected'}), 400

    if not job_description:
        return jsonify({'error': 'No job description provided'}), 400

    # Save the uploaded file temporarily
    filename = secure_filename(resume_file.filename)
    temp_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}_{filename}")
    resume_file.save(temp_path)

    try:
        # Extract text from PDF
        resume_text = extract_text_from_pdf(temp_path)

        # Tailor the resume using Gemini
        tailored_content = tailor_resume(resume_text, job_description)

        # Generate PDF with the selected template
        try:
            pdf_path = generate_pdf(tailored_content, template)

        except Exception as pdf_error:
            return jsonify({'error': f'Error generating PDF: {str(pdf_error)}'}), 500

        # In a real app, you would upload this to a storage service
        # and return a URL. For this example, we'll just return a placeholder.
        pdf_url = f"/download/{os.path.basename(pdf_path)}"

        response_data = {
            'success': True,
            'content': tailored_content,
            'pdf_url': pdf_url
        }
        return jsonify(response_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        # Clean up the temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    # In a real app, you would serve the file from your storage service
    # For this example, we'll just return a placeholder response
    return jsonify({'message': 'File download endpoint'}), 200

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Flask backend is running'}), 200

@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({'error': 'An unexpected error occurred', 'details': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

