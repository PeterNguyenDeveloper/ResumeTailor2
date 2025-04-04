from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile
import uuid
from werkzeug.utils import secure_filename
from services.pdf_parser import extract_text_from_pdf
from services.resume_tailor import tailor_resume
from services.pdf_generator import generate_pdf

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Create upload folder if it doesn't exist
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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

        print(f"Extracted resume text: {resume_text[:100]}...")  # Debugging line

        # Tailor the resume using Gemini
        tailored_content = tailor_resume(resume_text, job_description)

        print(f"Tailored content: {tailored_content[:100]}...")  # Debugging line

        # Generate PDF with the selected template
        pdf_path = generate_pdf(tailored_content, template)

        print(f"Generated PDF path: {pdf_path}")  # Debugging line

        # In a real app, you would upload this to a storage service
        # and return a URL. For this example, we'll just return a placeholder.
        pdf_url = f"/download/{os.path.basename(pdf_path)}"

        print(f"PDF URL: {pdf_url}")  # Debugging line

        return jsonify({
            'success': True,
            'content': tailored_content,
            'pdf_url': pdf_url
        })

    except Exception as e:
        print(f"Error: {str(e)}")  # Debugging line
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)