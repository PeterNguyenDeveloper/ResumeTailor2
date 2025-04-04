import google.generativeai as genai
import os
import html
import datetime
import re

# Helper function to get timestamp for print statements
def get_timestamp():
  return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# In a real application, you would get this from environment variables
API_KEY = os.environ.get("GEMINI_API_KEY", "your_api_key_here")

# Configure the Gemini API
genai.configure(api_key=API_KEY)

def tailor_resume(resume_text, job_description):
    """
    Use Google's Gemini to tailor the resume to the job description.

    Args:
        resume_text (str): Text extracted from the resume
        job_description (str): Job description text

    Returns:
        str: HTML content of the tailored resume
    """
    try:
        # Initialize the model
        model = genai.GenerativeModel('gemini-1.5-flash')

        # Create the prompt with specific instructions for WeasyPrint-compatible HTML
        prompt = f"""
        I need you to tailor a resume for a specific job and output it in HTML format that will be converted to PDF using WeasyPrint.

        Here is the original resume:
        {resume_text}

        Here is the job description:
        {job_description}

        Please analyze the job description and modify the resume to highlight relevant skills and experiences.
        Focus on:
        1. Matching keywords from the job description
        2. Highlighting relevant accomplishments
        3. Adjusting the summary/objective to match the job
        4. Prioritizing relevant experience

        IMPORTANT: Return a complete, well-structured HTML document that WeasyPrint can render properly.

        Follow these specific guidelines for the HTML:
        1. Include a proper DOCTYPE, <html>, <head>, and <body> tags
        2. Use semantic HTML5 elements
        3. Use <h1> for the name at the top of the resume
        4. Use a <p> with class="contact-info" for contact information
        5. Use <h2> for section headings (like "Experience", "Education", "Skills")
        6. Use <p> for paragraphs of text
        7. Use <ul> and <li> for lists of skills, accomplishments, etc.
        8. Use <div class="section"> to wrap each section
        9. Use <div class="divider"></div> to create separation between sections
        10. Keep the HTML clean and simple - WeasyPrint will apply the styling via CSS

        Example structure:
        ```html
        &lt;!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Tailored Resume</title>
        </head>
        <body>
            <h1>John Doe</h1>
            <p class="contact-info">email@example.com | (123) 456-7890 | City, State</p>

            <div class="section">
                <h2>Professional Summary</h2>
                <p>Experienced professional with expertise in...</p>
            </div>

            <div class="divider"></div>

            <div class="section">
                <h2>Experience</h2>
                <p><strong>Company Name</strong> - Position Title (Date - Date)</p>
                <ul>
                    <li>Accomplishment 1...</li>
                    <li>Accomplishment 2...</li>
                </ul>
            </div>

            &lt;!-- Additional sections... -->
        </body>
        </html>

