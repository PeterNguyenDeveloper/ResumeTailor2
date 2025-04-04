from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
import os
import uuid
import re
import html
import traceback

def generate_pdf(html_content, template):
    """
    Generate a PDF from HTML content using ReportLab.

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

        # Extract plain text content from HTML
        plain_content = extract_plain_content(html_content)

        # Create the PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            leftMargin=72,  # 1 inch
            rightMargin=72,
            topMargin=72,
            bottomMargin=72
        )

        # Get styles based on the template
        styles = get_template_styles(template)

        # Build the PDF content
        elements = []

        # Add name
        if plain_content.get('name'):
            elements.append(Paragraph(plain_content['name'], styles['name']))
            elements.append(Spacer(1, 12))

        # Add contact info
        if plain_content.get('contact_info'):
            elements.append(Paragraph(plain_content['contact_info'], styles['contact_info']))
            elements.append(Spacer(1, 24))

        # Add sections
        for section in plain_content.get('sections', []):
            # Add section heading
            if section.get('heading'):
                elements.append(Paragraph(section['heading'], styles['heading']))
                elements.append(Spacer(1, 8))

            # Add paragraphs
            for paragraph in section.get('paragraphs', []):
                # Clean the paragraph text to remove any potential issues
                clean_text = clean_text_for_reportlab(paragraph)
                if clean_text:
                    elements.append(Paragraph(clean_text, styles['normal']))
                    elements.append(Spacer(1, 6))

            # Add lists
            for list_items in section.get('lists', []):
                if list_items:
                    items = []
                    for item in list_items:
                        # Clean the list item text
                        clean_item = clean_text_for_reportlab(item)
                        if clean_item:
                            items.append(ListItem(Paragraph(clean_item, styles['list_item'])))

                    if items:
                        elements.append(ListFlowable(items, bulletType='bullet', leftIndent=20))
                        elements.append(Spacer(1, 6))

            # Add spacer after section
            elements.append(Spacer(1, 12))

        # Build the PDF
        doc.build(elements)

        # Verify the PDF was created successfully
        if not os.path.exists(output_path):
            raise Exception(f"PDF file was not created at {output_path}")

        if os.path.getsize(output_path) < 100:
            raise Exception(f"Generated PDF is too small ({os.path.getsize(output_path)} bytes)")

        return output_path

    except Exception as e:
        error_details = traceback.format_exc()
        raise Exception(f"Error generating PDF: {str(e)}\n{error_details}")

def clean_text_for_reportlab(text):
    """
    Clean text to avoid ReportLab issues with links and special characters.

    Args:
        text (str): Text to clean

    Returns:
        str: Cleaned text
    """
    if not text:
        return ""

    # Replace any HTML tags with their text content
    text = re.sub(r'<[^>]*>', ' ', text)

    # Decode HTML entities
    text = html.unescape(text)

    # Remove any potential link markers that might cause issues
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'www\.\S+', '', text)

    # Replace problematic characters
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')

    # Remove any control characters
    text = ''.join(c for c in text if ord(c) >= 32 or c in '\n\r\t')

    # Trim whitespace
    text = text.strip()

    return text

def extract_plain_content(html_content):
    """
    Extract plain text content from HTML for ReportLab.

    Args:
        html_content (str): HTML content

    Returns:
        dict: Structured plain text data
    """
    result = {
        'name': '',
        'contact_info': '',
        'sections': []
    }

    try:
        # Extract content between <body> tags if present
        body_match = re.search(r'<body>(.*?)</body>', html_content, re.DOTALL | re.IGNORECASE)
        if body_match:
            html_content = body_match.group(1)

        # Extract name (h1)
        name_match = re.search(r'<h1>(.*?)</h1>', html_content, re.DOTALL | re.IGNORECASE)
        if name_match:
            result['name'] = html.unescape(re.sub(r'<[^>]*>', '', name_match.group(1))).strip()

        # Extract contact info
        contact_match = re.search(r'<p class="contact-info">(.*?)</p>', html_content, re.DOTALL | re.IGNORECASE)
        if contact_match:
            result['contact_info'] = html.unescape(re.sub(r'<[^>]*>', '', contact_match.group(1))).strip()

        # Extract sections
        section_pattern = r'<div class="section">(.*?)</div>'
        section_matches = re.finditer(section_pattern, html_content, re.DOTALL | re.IGNORECASE)

        for section_match in section_matches:
            section_content = section_match.group(1)
            section = {
                'heading': '',
                'paragraphs': [],
                'lists': []
            }

            # Extract section heading
            heading_match = re.search(r'<h2>(.*?)</h2>', section_content, re.DOTALL | re.IGNORECASE)
            if heading_match:
                section['heading'] = html.unescape(re.sub(r'<[^>]*>', '', heading_match.group(1))).strip()

            # Extract paragraphs (excluding contact-info paragraphs)
            paragraph_pattern = r'<p(?!\s+class="contact-info")[^>]*>(.*?)</p>'
            paragraph_matches = re.finditer(paragraph_pattern, section_content, re.DOTALL | re.IGNORECASE)

            for paragraph_match in paragraph_matches:
                paragraph_text = paragraph_match.group(1).strip()
                clean_text = html.unescape(re.sub(r'<[^>]*>', '', paragraph_text)).strip()
                if clean_text:
                    section['paragraphs'].append(clean_text)

            # Extract lists
            list_pattern = r'<ul>(.*?)</ul>'
            list_matches = re.finditer(list_pattern, section_content, re.DOTALL | re.IGNORECASE)

            for list_match in list_matches:
                list_content = list_match.group(1)
                list_items = []

                item_pattern = r'<li>(.*?)</li>'
                item_matches = re.finditer(item_pattern, list_content, re.DOTALL | re.IGNORECASE)

                for item_match in item_matches:
                    item_text = item_match.group(1).strip()
                    clean_text = html.unescape(re.sub(r'<[^>]*>', '', item_text)).strip()
                    if clean_text:
                        list_items.append(clean_text)

                if list_items:
                    section['lists'].append(list_items)

            if section['heading'] or section['paragraphs'] or section['lists']:
                result['sections'].append(section)

    except Exception as e:
        # If there's an error in parsing, create a simple section with the error
        result['sections'] = [{
            'heading': 'Resume Content',
            'paragraphs': ['There was an error parsing the resume HTML. Please try again.'],
            'lists': []
        }]

    return result

def get_template_styles(template):
    """
    Get the styles for the selected template.

    Args:
        template (str): Template name

    Returns:
        dict: Styles for the template
    """
    # Get base styles
    styles = getSampleStyleSheet()

    # Common styles
    result = {
        'normal': ParagraphStyle(
            'Normal',
            parent=styles['Normal'],
            fontSize=10,
            leading=14
        ),
        'list_item': ParagraphStyle(
            'ListItem',
            parent=styles['Normal'],
            fontSize=10,
            leading=14
        )
    }

    # Template-specific styles
    if template == 'professional':
        result['name'] = ParagraphStyle(
            'Name',
            parent=styles['Title'],
            fontSize=16,
            textColor=colors.Color(0.17, 0.24, 0.31),  # #2c3e50
            alignment=TA_CENTER
        )
        result['contact_info'] = ParagraphStyle(
            'ContactInfo',
            parent=styles['Normal'],
            fontSize=9,
            alignment=TA_CENTER
        )
        result['heading'] = ParagraphStyle(
            'Heading',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.Color(0.16, 0.5, 0.73),  # #2980b9
            borderColor=colors.Color(0.2, 0.6, 0.86),  # #3498db
            borderWidth=0,
            borderPadding=0
        )

    elif template == 'creative':
        result['name'] = ParagraphStyle(
            'Name',
            parent=styles['Title'],
            fontSize=18,
            textColor=colors.Color(0.55, 0.27, 0.68),  # #8e44ad
            alignment=TA_CENTER
        )
        result['contact_info'] = ParagraphStyle(
            'ContactInfo',
            parent=styles['Normal'],
            fontSize=9,
            alignment=TA_CENTER
        )
        result['heading'] = ParagraphStyle(
            'Heading',
            parent=styles['Heading2'],
            fontSize=13,
            textColor=colors.Color(0.83, 0.33, 0),  # #d35400
            borderColor=colors.Color(0.9, 0.49, 0.13),  # #e67e22
            borderWidth=0,
            borderPadding=0
        )

    elif template == 'minimal':
        result['name'] = ParagraphStyle(
            'Name',
            parent=styles['Title'],
            fontSize=14,
            textColor=colors.Color(0.2, 0.2, 0.2),  # #333
            alignment=TA_CENTER
        )
        result['contact_info'] = ParagraphStyle(
            'ContactInfo',
            parent=styles['Normal'],
            fontSize=9,
            alignment=TA_CENTER
        )
        result['heading'] = ParagraphStyle(
            'Heading',
            parent=styles['Heading2'],
            fontSize=11,
            textColor=colors.Color(0.33, 0.33, 0.33),  # #555
            borderColor=colors.Color(0.87, 0.87, 0.87),  # #ddd
            borderWidth=0,
            borderPadding=0
        )
        result['normal'] = ParagraphStyle(
            'Normal',
            parent=styles['Normal'],
            fontSize=9,
            leading=12
        )
        result['list_item'] = ParagraphStyle(
            'ListItem',
            parent=styles['Normal'],
            fontSize=9,
            leading=12
        )

    elif template == 'executive':
        result['name'] = ParagraphStyle(
            'Name',
            parent=styles['Title'],
            fontSize=18,
            textColor=colors.Color(0.1, 0.1, 0.1),  # #1a1a1a
            alignment=TA_CENTER
        )
        result['contact_info'] = ParagraphStyle(
            'ContactInfo',
            parent=styles['Normal'],
            fontSize=9,
            alignment=TA_CENTER
        )
        result['heading'] = ParagraphStyle(
            'Heading',
            parent=styles['Heading2'],
            fontSize=13,
            textColor=colors.Color(0.1, 0.1, 0.1),  # #1a1a1a
            borderColor=colors.Color(0.1, 0.1, 0.1),  # #1a1a1a
            borderWidth=0,
            borderPadding=0
        )
        result['normal'] = ParagraphStyle(
            'Normal',
            parent=styles['Normal'],
            alignment=TA_JUSTIFY
        )

    else:
        # Default to professional if template not found
        return get_template_styles('professional')

    return result

