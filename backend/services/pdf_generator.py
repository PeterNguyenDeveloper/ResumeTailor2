from weasyprint import HTML
import tempfile
import os
import uuid
import traceback
import datetime

def generate_pdf(html_content, template):
    """
    Generate a PDF from HTML content using the selected template.

    Args:
        html_content (str): HTML content of the tailored resume
        template (str): Template name to use

    Returns:
        str: Path to the generated PDF file
    """
    try:
        # Apply the template (in a real app, you would have different CSS for each template)
        css_styles = get_template_css(template)

        # Create a complete HTML document with the CSS
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Tailored Resume</title>
            <style>
                {css_styles}
            </style>
        </head>
        <body>
            <div class="resume-container">
                {html_content}
            </div>
        </body>
        </html>
        """

        # Create output directory if it doesn't exist
        output_dir = 'generated_pdfs'
        os.makedirs(output_dir, exist_ok=True)

        # Generate a unique filename
        output_path = os.path.join(output_dir, f"{uuid.uuid4()}_resume.pdf")

        # Generate PDF - Fix the constructor call
        # Create a temporary HTML file
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False, mode='w', encoding='utf-8') as f:
            f.write(full_html)
            temp_html_path = f.name

        try:
            # Use the file path instead of the string parameter
            HTML(temp_html_path).write_pdf(output_path)
        finally:
            # Clean up the temporary HTML file
            if os.path.exists(temp_html_path):
                os.remove(temp_html_path)

        return output_path

    except Exception as e:
        raise Exception(f"Error generating PDF: {str(e)}")

def get_template_css(template):
    """
    Get the CSS styles for the selected template.

    Args:
        template (str): Template name

    Returns:
        str: CSS styles for the template
    """
    # Base styles for all templates
    base_css = """
        body {
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 0;
            color: #333;
        }
        .resume-container {
            max-width: 8.5in;
            margin: 0 auto;
            padding: 1in;
        }
        h1, h2, h3 {
            margin-top: 0;
        }
        ul {
            padding-left: 20px;
        }
    """

    # Template-specific styles
    if template == 'professional':
        return base_css + """
            h1 {
                color: #2c3e50;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
            }
            h2 {
                color: #2980b9;
                border-bottom: 1px solid #bdc3c7;
                padding-bottom: 5px;
            }
            .resume-container {
                line-height: 1.5;
            }
        """
    elif template == 'creative':
        return base_css + """
            h1 {
                color: #8e44ad;
                text-transform: uppercase;
                letter-spacing: 2px;
            }
            h2 {
                color: #d35400;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            .resume-container {
                line-height: 1.6;
                background-color: #f9f9f9;
                border-left: 5px solid #8e44ad;
            }
        """
    elif template == 'minimal':
        return base_css + """
            h1 {
                color: #333;
                font-weight: 300;
                letter-spacing: 1px;
            }
            h2 {
                color: #555;
                font-weight: 300;
                letter-spacing: 0.5px;
            }
            .resume-container {
                line-height: 1.4;
                font-weight: 300;
            }
        """
    elif template == 'executive':
        return base_css + """
            h1 {
                color: #1a1a1a;
                border-bottom: 3px double #1a1a1a;
                padding-bottom: 10px;
                text-transform: uppercase;
            }
            h2 {
                color: #1a1a1a;
                border-bottom: 1px solid #1a1a1a;
                padding-bottom: 5px;
            }
            .resume-container {
                line-height: 1.5;
                font-family: 'Georgia', serif;
            }
        """
    else:
        # Default to professional if template not found
        return base_css

