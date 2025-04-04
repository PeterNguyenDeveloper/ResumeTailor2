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

        # Create the prompt
        prompt = create_prompt(resume_text, job_description)

        # Generate the tailored resume
        response = model.generate_content(prompt)

        # Extract the HTML content
        html_content = response.text

        # Process the HTML content
        html_content = process_html_content(html_content)

        return html_content

    except Exception as e:
        raise Exception(f"Error tailoring resume with Gemini: {str(e)}")

def create_prompt(resume_text, job_description):
    """Create the prompt for Gemini AI."""
    prompt = (
        "I need you to tailor a resume for a specific job and output it in HTML format "
        "that will be converted to PDF using WeasyPrint.\n\n"

        f"Here is the original resume:\n{resume_text}\n\n"

        f"Here is the job description:\n{job_description}\n\n"

        "Please analyze the job description and modify the resume to highlight relevant skills and experiences.\n"
        "Focus on:\n"
        "1. Matching keywords from the job description\n"
        "2. Highlighting relevant accomplishments\n"
        "3. Adjusting the summary/objective to match the job\n"
        "4. Prioritizing relevant experience\n\n"

        "IMPORTANT: Return a complete, well-structured HTML document that WeasyPrint can render properly.\n\n"

        "Follow these specific guidelines for the HTML:\n"
        "1. Include a proper DOCTYPE, <html>, <head>, and <body> tags\n"
        "2. Use semantic HTML5 elements\n"
        "3. Use <h1> for the name at the top of the resume\n"
        "4. Use a <p> with class=\"contact-info\" for contact information\n"
        "5. Use <h2> for section headings (like \"Experience\", \"Education\", \"Skills\")\n"
        "6. Use <p> for paragraphs of text\n"
        "7. Use <ul> and <li> for lists of skills, accomplishments, etc.\n"
        "8. Use <div class=\"section\"> to wrap each section\n"
        "9. Use <div class=\"divider\"></div> to create separation between sections\n"
        "10. Keep the HTML clean and simple - WeasyPrint will apply the styling via CSS\n\n"

        "Return ONLY the HTML document, with no additional text, explanations, or markdown formatting."
    )
    return prompt

def process_html_content(html_content):
    """Process and clean up the HTML content from Gemini."""
    # Check if the content is wrapped in code blocks and extract it
    if "```html" in html_content and "```" in html_content:
        # Extract content between ```html and ```
        match = re.search(r'```html\s*(.*?)\s*```', html_content, re.DOTALL)
        if match:
            html_content = match.group(1)
    elif "```" in html_content:
        # Extract content between ``` and ```
        match = re.search(r'```\s*(.*?)\s*```', html_content, re.DOTALL)
        if match:
            html_content = match.group(1)

    # Ensure the content has basic HTML structure
    if not html_content.strip().startswith('<!DOCTYPE') and not html_content.strip().startswith('<html'):
        # If it's not a complete HTML document, wrap it in proper HTML structure
        html_content = (
            "<!DOCTYPE html>\n"
            "<html>\n"
            "<head>\n"
            "    <meta charset=\"UTF-8\">\n"
            "    <title>Tailored Resume</title>\n"
            "</head>\n"
            "<body>\n"
            f"{html_content}\n"
            "</body>\n"
            "</html>"
        )

    return html_content

