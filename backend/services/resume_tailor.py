import google.generativeai as genai
import os
import html
import datetime

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
        print(f"[{get_timestamp()}] Initializing Gemini model", flush=True)
        # Initialize the model
        model = genai.GenerativeModel('gemini-2.5-pro-exp-03-25')

        # Create the prompt
        print(f"[{get_timestamp()}] Creating prompt for Gemini", flush=True)
        prompt = f"""
        I need you to tailor a resume for a specific job.

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

        Return the result as clean HTML that can be rendered in a browser. Use appropriate HTML tags for structure (h1, h2, p, ul, li, etc.).
        Do not include any explanations or notes, just the formatted HTML content of the tailored resume.
        """

        # Generate the tailored resume
        print(f"[{get_timestamp()}] Sending request to Gemini API", flush=True)
        response = model.generate_content(prompt)

        # Extract and clean the HTML content
        html_content = response.text
        print(f"[{get_timestamp()}] Received response from Gemini API: {len(html_content)} characters", flush=True)

        # Basic sanitization (in a real app, use a proper HTML sanitizer)
        html_content = html.escape(html_content).replace('\n', '<br>')
        print(f"[{get_timestamp()}] Sanitized HTML content", flush=True)

        return html_content

    except Exception as e:
        print(f"[{get_timestamp()}] ERROR tailoring resume with Gemini: {str(e)}", flush=True)
        raise Exception(f"Error tailoring resume with Gemini: {str(e)}")

