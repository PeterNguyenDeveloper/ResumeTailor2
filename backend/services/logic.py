import os
import google.generativeai as genai
import PyPDF2
import uuid
from xhtml2pdf import pisa

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                page_text = page.extract_text()
                text += page_text
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")
    return text

def create_prompt(resume_text, job_description, template):
    """Create the prompt for Gemini AI."""
    prompt = (
        "I need you to tailor a resume for a specific job and output it in a well-structured HTML format "
        "that will be converted to PDF using PyPDF2.\n\n"

        f"Here is the original resume:\n{resume_text}\n\n"

        f"Here is the job description:\n{job_description}\n\n"

        f"Style the resume in a {template} template.\n\n"

        "Please analyze the job description and modify the resume to highlight relevant skills and experiences.\n"
        "Focus on:\n"
        "1. Matching keywords from the job description\n"
        "2. Highlighting relevant accomplishments\n"
        "3. Adjusting the summary/objective to match the job\n"
        "4. Prioritizing relevant experience\n"
        "5. Maintain original formatting with bullets points\n"
        "6. Try to keep resulting HTML to one pdf page\n"
        "7. Try to have at least 15 words on each line\n"
        "8. DO NOT ADD YOUR COMMENTS, TREAT AS FINAL DRAFT\n\n"

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
        "10. No CSS Styles\n"

        "Return ONLY the HTML document, with no additional text, explanations, or markdown formatting."
    )
    return prompt

def tailor_resume(resume_text, job_description, api_key, template):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = create_prompt(resume_text, job_description, template)
    response = model.generate_content(prompt)
    return clean_response(response.text)

def clean_response(response_text):
    cleaned_text = response_text.strip()
    if cleaned_text.startswith("```html") and cleaned_text.endswith("```"):
        cleaned_text = cleaned_text[7:-3].strip()
    elif cleaned_text.startswith("```") and cleaned_text.endswith("```"):
        cleaned_text = cleaned_text[3:-3].strip()
    return cleaned_text

def generate_pdf(tailored_content):
    output_dir = 'generated_pdfs'
    os.makedirs(output_dir, exist_ok=True)
    output_pdf = f"{uuid.uuid4()}_resume.pdf"
    with open(os.path.join(output_dir, output_pdf), "wb") as pdf_file:
        pisa.CreatePDF( tailored_content, dest=pdf_file)
    return output_pdf