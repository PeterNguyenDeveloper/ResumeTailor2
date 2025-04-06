from flask import Flask, request, jsonify, make_response, send_from_directory, Response, stream_with_context
from flask_cors import CORS
import re
import os
import uuid
import json
import traceback
import time
from werkzeug.utils import secure_filename
from services.logic import extract_text_from_pdf
from services.logic import tailor_resume
from services.logic import generate_pdf
import google.generativeai as genai

app = Flask(__name__)

# Allow only your frontend's origin to prevent issues
CORS(app, origins=["http://137.184.12.12:3000"])

# Create necessary folders
UPLOAD_FOLDER = 'uploaded_files'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

#init genai
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

@app.route("/api/stream-tailor-resume", methods=["POST"])
def stream_tailor_resume():

    resume_file = request.files.get("resume")
    job_description = request.form.get("job_description")
    template = request.form.get("template")  # optional

    if not resume_file or not job_description:
        return "Missing resume or job description", 400

    try:

        filename = secure_filename(resume_file.filename)
        temp_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}_{filename}")
        resume_file.save(temp_path)
        file_part = genai.upload_file(temp_path)

        prompt = (
            "Respond in Markdown format. Output the finished resume. "
            "Each line should be between 15 to 30 words. Don't omit anything from original resume. "
            "Tailor the resume to the following Job Description: " + job_description
        )

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content([prompt, file_part], stream=True)

        def generate():
            for chunk in response:
                if chunk.text:
                    word = ""
                    for char in chunk.text:  # Process each character in the text
                        if char.isspace():  # If the character is a whitespace (space, tab, newline)
                            if word:  # If there's a word accumulated, yield it first
                                yield word
                                time.sleep(0.01)  # Optional delay for smoother stream
                                word = ""  # Reset the word accumulator
                            yield char  # Yield the whitespace character
                        else:
                            word += char  # Accumulate characters into a word
                    if word:  # Yield any remaining word after processing all characters
                        yield word
                        time.sleep(0.01)  # Optional delay for smoother stream

        return Response(stream_with_context(generate()), mimetype="text/plain")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

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
    app.run(host='0.0.0.0', port=5000)
