from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
import os
import uuid
import tempfile
import traceback

def generate_pdf(html_content, template):
    """
    Generate a PDF from HTML content using WeasyPrint.

    Args:
        html_content (str): HTML content of the tailored resume
        template (str): Template name to use

    Returns:
        str: Path to the generated PDF file
    """
    try:
        # Create output directory if it doesn't exist
        output_dir = 'generated_pdfs'
        os.makedirs(output_dir, exist_ok=True)

        # Generate a unique filename
        output_path = os.path.join(output_dir, f"{uuid.uuid4()}_resume.pdf")

        # Get CSS for the selected template
        css_content = get_template_css(template)

        # Create a temporary CSS file
        with tempfile.NamedTemporaryFile(suffix='.css', delete=False, mode='w', encoding='utf-8') as css_file:
            css_file.write(css_content)
            css_path = css_file.name

        try:
            # Configure fonts
            font_config = FontConfiguration()

            # Create CSS object
            css = CSS(filename=css_path, font_config=font_config)

            # Ensure the HTML has proper structure
            if "<html" not in html_content:
                html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>Tailored Resume</title>
                </head>
                <body>
                    {html_content}
                </body>
                </html>
                """

            # Create a temporary HTML file
            with tempfile.NamedTemporaryFile(suffix='.html', delete=False, mode='w', encoding='utf-8') as html_file:
                html_file.write(html_content)
                html_path = html_file.name

            # Generate PDF
            HTML(filename=html_path).write_pdf(
                output_path,
                stylesheets=[css],
                font_config=font_config
            )

            # Check if the PDF was created successfully
            if not os.path.exists(output_path) or os.path.getsize(output_path) < 100:
                raise Exception("Generated PDF is empty or invalid")

            return output_path

        finally:
            # Clean up temporary files
            if os.path.exists(css_path):
                os.remove(css_path)
            if os.path.exists(html_path):
                os.remove(html_path)

    except Exception as e:
        error_details = traceback.format_exc()
        raise Exception(f"Error generating PDF: {str(e)}\n{error_details}")

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
        @page {
            size: letter;
            margin: 0.5in;
        }

        body {
            font-family: 'Times New Roman', serif;
            margin: 0;
            padding: 0;
            color: #333;
            line-height: 1.5;
        }

        h1 {
            margin-top: 0;
            text-align: center;
        }

        h2 {
            margin-top: 1em;
            border-bottom: 1px solid #ddd;
            padding-bottom: 0.2em;
        }

        p {
            margin: 0.5em 0;
            text-align: justify;
        }

        ul {
            margin: 0.5em 0;
            padding-left: 1.5em;
        }

        li {
            margin-bottom: 0.25em;
        }

        .contact-info {
            text-align: center;
            font-size: 0.9em;
            margin-bottom: 1em;
        }

        .section {
            margin-bottom: 1em;
        }

        .divider {
            border-top: 1px solid #ddd;
            margin: 1em 0;
        }
    """

    # Template-specific styles
    if template == 'professional':
        return base_css + """
            body {
                font-family: 'Arial', 'Helvetica', sans-serif;
            }

            h1 {
                color: #2c3e50;
                font-size: 1.5em;
            }

            h2 {
                color: #2980b9;
                font-size: 1.2em;
                border-bottom: 1px solid #3498db;
            }

            .divider {
                border-top: 1px solid #3498db;
            }
        """
    elif template == 'creative':
        return base_css + """
            body {
                font-family: 'Georgia', serif;
            }

            h1 {
                color: #8e44ad;
                font-size: 1.6em;
                text-transform: uppercase;
                letter-spacing: 2px;
            }

            h2 {
                color: #d35400;
                font-size: 1.3em;
                text-transform: uppercase;
                letter-spacing: 1px;
                border-bottom: 1px solid #e67e22;
            }

            .divider {
                border-top: 1px solid #d35400;
            }
        """
    elif template == 'minimal':
        return base_css + """
            body {
                font-family: 'Helvetica', 'Arial', sans-serif;
                font-weight: 300;
            }

            h1 {
                color: #333;
                font-size: 1.4em;
                font-weight: 400;
                letter-spacing: 1px;
            }

            h2 {
                color: #555;
                font-size: 1.1em;
                font-weight: 400;
                letter-spacing: 0.5px;
                border-bottom: 1px solid #ddd;
            }

            p, li {
                font-size: 0.9em;
            }

            .divider {
                border-top: 1px solid #ddd;
            }
        """
    elif template == 'executive':
        return base_css + """
            body {
                font-family: 'Times New Roman', serif;
            }

            h1 {
                color: #1a1a1a;
                font-size: 1.6em;
                border-bottom: 3px double #1a1a1a;
                padding-bottom: 0.3em;
                text-transform: uppercase;
            }

            h2 {
                color: #1a1a1a;
                font-size: 1.2em;
                border-bottom: 1px solid #1a1a1a;
            }

            .divider {
                border-top: 1px solid #1a1a1a;
            }
        """
    else:
        # Default to professional if template not found
        return get_template_css('professional')

