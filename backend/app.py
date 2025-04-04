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
    logger.info("Received tailor-resume request")

    try:
        if 'resume' not in request.files:
            logger.error("No resume file provided")
            return jsonify({'error': 'No resume file provided'}), 400

        resume_file = request.files['resume']
        job_description = request.form.get('job_description', '')
        template = request.form.get('template', 'professional')

        logger.info(f"Resume filename: {resume_file.filename}, Template: {template}")

        if not resume_file or resume_file.filename == '':
            logger.error("No resume file selected")
            return jsonify({'error': 'No resume file selected'}), 400

        if not job_description:
            logger.error("No job description provided")
            return jsonify({'error': 'No job description provided'}), 400

        # Save the uploaded file temporarily
        filename = secure_filename(resume_file.filename)
        temp_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}_{filename}")
        resume_file.save(temp_path)
        logger.info(f"Saved resume to: {temp_path}")

        try:
            # Extract text from PDF
            logger.info("Extracting text from PDF")
            resume_text = extract_text_from_pdf(temp_path)
            logger.info(f"Extracted {len(resume_text)} characters from PDF")

            # Tailor the resume using Gemini
            logger.info("Tailoring resume with Gemini")
            tailored_content = tailor_resume(resume_text, job_description)
            logger.info("Successfully tailored resume")

            # Generate PDF with the selected template
            logger.info(f"Generating PDF with {template} template")
            try:
                pdf_path = generate_pdf(tailored_content, template)
                logger.info(f"Generated PDF at: {pdf_path}")

            except Exception as pdf_error:
                logger.error(f"Error generating PDF: {str(pdf_error)}")
                logger.error(traceback.format_exc())
                return jsonify({'error': f'Error generating PDF: {str(pdf_error)}'}), 500

            # In a real app, you would upload this to a storage service
            # and return a URL. For this example, we'll just return a placeholder.
            pdf_url = f"/download/{os.path.basename(pdf_path)}"

            response_data = {
                'success': True,
                'content': tailored_content,
                'pdf_url': pdf_url
            }
            logger.info("Successfully processed request")
            return jsonify(response_data)

        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({'error': str(e)}), 500

        finally:
            # Clean up the temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                logger.info(f"Removed temporary file: {temp_path}")

    except Exception as outer_e:
        logger.error(f"Unexpected error: {str(outer_e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': f'Unexpected error: {str(outer_e)}'}), 500

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    logger.info(f"Download request for file: {filename}")
    # In a real app, you would serve the file from your storage service
    # For this example, we'll just return a placeholder response
    return jsonify({'message': 'File download endpoint'}), 200

@app.route('/api/health', methods=['GET'])
def health_check():
    logger.info("Health check request")
    return jsonify({'status': 'healthy', 'message': 'Flask backend is running'}), 200

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {str(e)}")
    logger.error(traceback.format_exc())
    return jsonify({'error': 'An unexpected error occurred', 'details': str(e)}), 500

if __name__ == '__main__':
    logger.info("Starting Flask application")
    # Check if Gemini API key is set
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.warning("GEMINI_API_KEY environment variable is not set!")
    else:
        logger.info("GEMINI_API_KEY is configured")

    app.run(host='0.0.0.0', port=5000, debug=True)

