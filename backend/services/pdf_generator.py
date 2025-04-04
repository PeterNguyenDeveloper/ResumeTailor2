from weasyprint import HTML, CSS
import os
import uuid
import tempfile
import traceback
import logging

# Configure WeasyPrint logging
logging.getLogger('weasyprint').setLevel(logging.ERROR)

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
        pdf_filename = f"{uuid.uuid4()}_resume.pdf"
        output_path = os.path.join(output_dir, pdf_filename)

        # Get CSS for the selected template
        css_content = get_template_css(template)

        # Create temporary files
        html_path = None
        css_path = None

        try:
            # Create a temporary file for the HTML content
            with tempfile.NamedTemporaryFile(suffix='.html', delete=False, mode='w', encoding='utf-8') as html_file:
                html_file.write(html_content)
                html_path = html_file.name

            # Create a temporary file for the CSS content
            with tempfile.NamedTemporaryFile(suffix='.css', delete=False, mode='w', encoding='utf-8') as css_file:
                css_file.write(css_content)
                css_path = css_file.name

            # Generate the PDF using WeasyPrint
            # Use a simpler approach that's compatible with older versions
            html = HTML(filename=html_path)
            css = CSS(filename=css_path)

            # Render the PDF - use a simpler call that works with older versions
            document = html.render(stylesheets=[css])
            document.write_pdf(target=output_path)

            # Verify the PDF was created successfully
            if not os.path.exists(output_path):
                raise Exception(f"PDF file was not created at {output_path}")

            if os.path.getsize(output_path) < 100:
                raise Exception(f"Generated PDF is too small ({os.path.getsize(output_path)} bytes)")

            return output_path

        except Exception as e:
            error_msg = str(e)
            raise Exception(f"WeasyPrint error: {error_msg}")

        finally:
            # Clean up temporary files
            for path in [html_path, css_path]:
                if path and os.path.exists(path):
                    try:
                        os.remove(path)
                    except:
                        pass

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
            margin: 0.75in 0.75in 0.75in 0.75in;
        }

        * {
            box-sizing: border-box;
        }

        body {
            font-family: 'Times New Roman', serif;
            margin: 0;
            padding: 0;
            color: #333;
            line-height: 1.5;
            font-size: 10pt;
        }

        h1 {
            margin-top: 0;
            margin-bottom: 0.3em;
            text-align: center;
            font-size: 16pt;
        }

        h2 {
            margin-top: 1em;
            margin-bottom: 0.5em;
            border-bottom: 1px solid #ddd;
            padding-bottom: 0.2em;
            font-size: 12pt;
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
            font-size: 9pt;
            margin-bottom: 1em;
        }

        .section {
            margin-bottom: 1em;
        }

        .divider {
            border-top: 1px solid #ddd;
            margin: 1em 0;
        }

        strong, b {
            font-weight: bold;
        }

        em, i {
            font-style: italic;
        }
    """

    # Template-specific styles
    if template == 'professional':
        return base_css + """
            body {
                font-family: Arial, Helvetica, sans-serif;
            }

            h1 {
                color: #2c3e50;
                font-size: 16pt;
            }

            h2 {
                color: #2980b9;
                font-size: 12pt;
                border-bottom: 1px solid #3498db;
            }

            .divider {
                border-top: 1px solid #3498db;
            }

            .section {
                margin-bottom: 1.2em;
            }
        """
    elif template == 'creative':
        return base_css + """
            body {
                font-family: Georgia, serif;
            }

            h1 {
                color: #8e44ad;
                font-size: 18pt;
                text-transform: uppercase;
                letter-spacing: 2px;
            }

            h2 {
                color: #d35400;
                font-size: 13pt;
                text-transform: uppercase;
                letter-spacing: 1px;
                border-bottom: 1px solid #e67e22;
            }

            .divider {
                border-top: 1px solid #d35400;
            }

            .section {
                margin-bottom: 1.5em;
            }
        """
    elif template == 'minimal':
        return base_css + """
            body {
                font-family: Helvetica, Arial, sans-serif;
                font-weight: 300;
                line-height: 1.4;
            }

            h1 {
                color: #333;
                font-size: 14pt;
                font-weight: 400;
                letter-spacing: 1px;
            }

            h2 {
                color: #555;
                font-size: 11pt;
                font-weight: 400;
                letter-spacing: 0.5px;
                border-bottom: 1px solid #ddd;
            }

            p, li {
                font-size: 9pt;
            }

            .divider {
                border-top: 1px solid #ddd;
            }

            .section {
                margin-bottom: 1em;
            }
        """
    elif template == 'executive':
        return base_css + """
            body {
                font-family: 'Times New Roman', serif;
                line-height: 1.6;
            }

            h1 {
                color: #1a1a1a;
                font-size: 18pt;
                border-bottom: 3px double #1a1a1a;
                padding-bottom: 0.3em;
                text-transform: uppercase;
            }

            h2 {
                color: #1a1a1a;
                font-size: 13pt;
                border-bottom: 1px solid #1a1a1a;
            }

            .divider {
                border-top: 1px solid #1a1a1a;
            }

            .section {
                margin-bottom: 1.5em;
            }

            strong, b {
                font-weight: bold;
            }
        """
    else:
        # Default to professional if template not found
        return get_template_css('professional')

