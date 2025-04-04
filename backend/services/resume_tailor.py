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
        "I need you to tailor a resume for a specific job and output it in a well-structured HTML format "
        "that will be converted to PDF using ReportLab.\n\n"

        f"Here is the original resume:\n{resume_text}\n\n"

        f"Here is the job description:\n{job_description}\n\n"

        "Please analyze the job description and modify the resume to highlight relevant skills and experiences.\n"
        "Focus on:\n"
        "1. Matching keywords from the job description\n"
        "2. Highlighting relevant accomplishments\n"
        "3. Adjusting the summary/objective to match the job\n"
        "4. Prioritizing relevant experience\n\n"

        "IMPORTANT: Return a well-structured HTML document that follows these specific guidelines:\n\n"

        "1. Include a proper DOCTYPE, <html>, <head>, and <body> tags\n"
        "2. Use <h1> for the name at the top of the resume\n"
        "3. Use a <p> with class=\"contact-info\" for contact information\n"
        "4. Use <div class=\"section\"> to wrap each section\n"
        "5. Use <h2> for section headings (like \"Experience\", \"Education\", \"Skills\")\n"
        "6. For experience entries, use this structure:\n"
        "   <p><strong>Job Title</strong> at <strong>Company</strong>, Location | Date</p>\n"
        "   <p>Brief description of role</p>\n"
        "   <ul>\n"
        "     <li>Achievement/responsibility 1</li>\n"
        "     <li>Achievement/responsibility 2</li>\n"
        "   </ul>\n"
        "7. For education entries, use this structure:\n"
        "   <p><strong>Degree</strong>, <strong>Institution</strong>, Location | Date</p>\n"
        "   <p>Additional details (GPA, honors, etc.)</p>\n"
        "8. For skills, use either:\n"
        "   <p><strong>Category:</strong> Skill 1, Skill 2, Skill 3</p>\n"
        "   or a simple list:\n"
        "   <ul>\n"
        "     <li>Skill 1</li>\n"
        "     <li>Skill 2</li>\n"
        "   </ul>\n"
        "9. DO NOT use any links, images, tables, or complex formatting\n"
        "10. DO NOT use any inline styles or CSS\n\n"

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

    # Clean up any potential issues that might cause problems with ReportLab
    html_content = clean_html_for_reportlab(html_content)

    return html_content

def clean_html_for_reportlab(html_content):
    """Clean HTML content to make it more compatible with ReportLab."""
    # Remove any <a> tags but keep their content
    html_content = re.sub(r'<a[^>]*>(.*?)</a>', r'\1', html_content, flags=re.DOTALL)

    # Remove any <style> tags and their content
    html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL)

    # Remove any <script> tags and their content
    html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL)

    # Remove any inline styles
    html_content = re.sub(r' style="[^"]*"', '', html_content)

    # Remove any class attributes except for "contact-info" and "section"
    def clean_class(match):
        if 'contact-info' in match.group(1) or 'section' in match.group(1):
            return match.group(0)
        return ''

    html_content = re.sub(r' class="([^"]*)"', clean_class, html_content)

    # Remove any other attributes that might cause issues
    html_content = re.sub(r' (id|onclick|onload|href|src)="[^"]*"', '', html_content)

    return html_content

