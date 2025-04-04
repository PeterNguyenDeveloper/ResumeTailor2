from flask import Flask, request, jsonify, make_response, send_from_directory
from flask_cors import CORS
import os
import tempfile
import uuid
import json
import traceback
from werkzeug.utils import secure_filename
from services.pdf_parser import extract_text_from_pdf
from services.resume_tailor import tailor_resume
from services.pdf_generator import generate_pdf

app = Flask(__name__)
# Allow all origins for CORS
CORS(app, resources={r"/*": {"origins": "*"}})

# Create necessary folders
UPLOAD_FOLDER = 'uploads'
PDF_FOLDER = 'generated_pdfs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PDF_FOLDER, exist_ok=True)

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
    try:
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

            # Check Gemini API key
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                return jsonify({'error': 'GEMINI_API_KEY not configured'}), 500

            # Tailor the resume using Gemini
            try:
                tailored_content = tailor_resume(resume_text, job_description)
            except Exception as gemini_error:
                return jsonify({'error': f'Error with Gemini API: {str(gemini_error)}'}), 500

            # Generate PDF with the selected template
            try:
                pdf_path = generate_pdf(tailored_content, template)
                pdf_filename = os.path.basename(pdf_path)
            except Exception as pdf_error:
                return jsonify({'error': f'Error generating PDF: {str(pdf_error)}'}), 500

            # Create a download URL for the PDF
            pdf_url = f"/api/download/{pdf_filename}"

            response_data = {
                'success': True,
                'content': tailored_content,
                'pdf_url': pdf_url,
                'pdf_filename': pdf_filename
            }
            return jsonify(response_data)

        except Exception as e:
            return jsonify({'error': str(e)}), 500

        finally:
            # Clean up the temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)

    except Exception as outer_e:
        return jsonify({'error': f'Unexpected error: {str(outer_e)}'}), 500

@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    """
    Serve the generated PDF file for download.
    """
    try:
        # Set the appropriate headers for a PDF download
        response = send_from_directory(
            PDF_FOLDER,
            filename,
            as_attachment=True,
            mimetype='application/pdf'
        )
        response.headers["Content-Disposition"] = f"attachment; filename={filename}"
        return response
    except Exception as e:
        return jsonify({'error': f'Error downloading file: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Flask backend is running'}), 200

@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({'error': 'An unexpected error occurred', 'details': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

