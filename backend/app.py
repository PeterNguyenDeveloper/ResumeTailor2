from flask import Flask, request, jsonify, make_response, send_from_directory
from flask_cors import CORS
import os
import uuid
import json
import traceback
from werkzeug.utils import secure_filename
from services.logic import extract_text_from_pdf
from services.logic import tailor_resume
from services.logic import generate_pdf

app = Flask(__name__)

# Configure CORS to allow requests from any origin
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
        if 'job_description' not in request.form:
            return jsonify({'error': 'No job description provided'}), 400

        resume_file = request.files['resume']
        job_description = request.form.get('job_description')
        template = request.form.get('template', 'professional')

        # Save the uploaded file temporarily
        filename = secure_filename(resume_file.filename)
        temp_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}_{filename}")
        resume_file.save(temp_path)

        try:
            resume_text = extract_text_from_pdf(temp_path)
            api_key = os.environ.get("GEMINI_API_KEY")
            tailored_content = tailor_resume(resume_text, job_description,api_key)
            pdf_filename = generate_pdf(tailored_content)

            response_data = {
                'success': True,
                'content': tailored_content,
                'pdf_url': f"/api/download/{pdf_filename}",
                'pdf_filename': pdf_filename
            }
            return jsonify(response_data)

        except Exception as e:
            error_details = traceback.format_exc()
            return jsonify({
                'error': str(e),
                'details': error_details
            }), 500

        finally:
            # Clean up the temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)

    except Exception as outer_e:
        error_details = traceback.format_exc()
        return jsonify({
            'error': f'Unexpected error: {str(outer_e)}',
            'details': error_details
        }), 500

@app.route('/api/download/<filename>', methods=['GET', 'OPTIONS'])
def download_file(filename):
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
        return response

    try:
        # Check if the file exists
        file_path = os.path.join(PDF_FOLDER, filename)
        if not os.path.exists(file_path):
            return jsonify({'error': f'File not found: {filename}'}), 404

        # Set the appropriate headers for a PDF download
        response = send_from_directory(
            PDF_FOLDER,
            filename,
            as_attachment=True,
            mimetype='application/pdf'
        )
        response.headers["Content-Disposition"] = f"attachment; filename={filename}"
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response
    except Exception as e:
        error_details = traceback.format_exc()
        return jsonify({
            'error': f'Error downloading file: {str(e)}',
            'details': error_details
        }), 500

# Custom error handler for all exceptions
@app.errorhandler(Exception)
def handle_exception(e):
    # Log the error
    error_details = traceback.format_exc()

    # Return JSON instead of HTML for HTTP errors
    return jsonify({
        "error": "An unexpected error occurred",
        "details": str(e),
        "traceback": error_details
    }), 500

# Custom 404 handler
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found", "details": str(e)}), 404

# Custom 405 handler
@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Method not allowed", "details": str(e)}), 405

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)