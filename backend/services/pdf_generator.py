from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListItem, ListFlowable, HRFlowable
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

        # Parse the HTML content to extract structured data
        parsed_content = parse_html_content(html_content)

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

        # Add name (h1)
        if parsed_content.get('name'):
            elements.append(Paragraph(parsed_content['name'], styles['name']))
            elements.append(Spacer(1, 6))

        # Add contact info
        if parsed_content.get('contact_info'):
            elements.append(Paragraph(parsed_content['contact_info'], styles['contact_info']))
            elements.append(Spacer(1, 12))

        # Add sections
        for section in parsed_content.get('sections', []):
            # Add section heading
            if section.get('heading'):
                elements.append(Paragraph(section['heading'], styles['heading']))
                elements.append(Spacer(1, 6))

            # Add section content
            for content in section.get('content', []):
                if content['type'] == 'paragraph':
                    elements.append(Paragraph(content['text'], styles['normal']))
                    elements.append(Spacer(1, 6))
                elif content['type'] == 'list':
                    list_items = []
                    for item in content['items']:
                        list_items.append(ListItem(Paragraph(item, styles['list_item'])))
                    elements.append(ListFlowable(list_items, bulletType='bullet', leftIndent=20))
                    elements.append(Spacer(1, 6))

            # Add divider after section
            elements.append(HRFlowable(width="100%", thickness=1, color=styles['divider_color'], spaceBefore=6, spaceAfter=12))

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

def parse_html_content(html_content):
    """
    Parse the HTML content to extract structured data for ReportLab.

    Args:
        html_content (str): HTML content

    Returns:
        dict: Structured data extracted from HTML
    """
    result = {
        'name': '',
        'contact_info': '',
        'sections': []
    }

    # Extract content between <body> tags if present
    body_match = re.search(r'<body>(.*?)</body>', html_content, re.DOTALL | re.IGNORECASE)
    if body_match:
        html_content = body_match.group(1)

    # Extract name (h1)
    name_match = re.search(r'<h1>(.*?)</h1>', html_content, re.DOTALL | re.IGNORECASE)
    if name_match:
        result['name'] = html.unescape(name_match.group(1).strip())

    # Extract contact info
    contact_match = re.search(r'<p class="contact-info">(.*?)</p>', html_content, re.DOTALL | re.IGNORECASE)
    if contact_match:
        result['contact_info'] = html.unescape(contact_match.group(1).strip())

    # Extract sections
    section_pattern = r'<div class="section">(.*?)</div>'
    section_matches = re.finditer(section_pattern, html_content, re.DOTALL | re.IGNORECASE)

    for section_match in section_matches:
        section_content = section_match.group(1)
        section = {'heading': '', 'content': []}

        # Extract section heading
        heading_match = re.search(r'<h2>(.*?)</h2>', section_content, re.DOTALL | re.IGNORECASE)
        if heading_match:
            section['heading'] = html.unescape(heading_match.group(1).strip())

        # Extract paragraphs
        paragraph_pattern = r'<p(?:\s+[^>]*)?>(.*?)</p>'
        paragraph_matches = re.finditer(paragraph_pattern, section_content, re.DOTALL | re.IGNORECASE)

        for paragraph_match in paragraph_matches:
            paragraph_text = paragraph_match.group(1).strip()
            if 'class="contact-info"' not in paragraph_match.group(0):  # Skip contact info
                section['content'].append({
                    'type': 'paragraph',
                    'text': html.unescape(paragraph_text)
                })

        # Extract lists
        list_pattern = r'<ul>(.*?)</ul>'
        list_matches = re.finditer(list_pattern, section_content, re.DOTALL | re.IGNORECASE)

        for list_match in list_matches:
            list_content = list_match.group(1)
            list_items = []

            item_pattern = r'<li>(.*?)</li>'
            item_matches = re.finditer(item_pattern, list_content, re.DOTALL | re.IGNORECASE)

            for item_match in item_matches:
                list_items.append(html.unescape(item_match.group(1).strip()))

            if list_items:
                section['content'].append({
                    'type': 'list',
                    'items': list_items
                })

        result['sections'].append(section)

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
        'normal': styles['Normal'],
        'list_item': styles['Normal'],
        'divider_color': colors.gray
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
            borderWidth=1,
            borderColor=colors.Color(0.2, 0.6, 0.86),  # #3498db
            borderPadding=(0, 0, 2, 0)
        )
        result['divider_color'] = colors.Color(0.2, 0.6, 0.86)  # #3498db

    elif template == 'creative':
        result['name'] = ParagraphStyle(
            'Name',
            parent=styles['Title'],
            fontSize=18,
            textColor=colors.Color(0.55, 0.27, 0.68),  # #8e44ad
            alignment=TA_CENTER,
            textTransform='uppercase',
            letterSpacing=2
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
            textTransform='uppercase',
            letterSpacing=1,
            borderWidth=1,
            borderColor=colors.Color(0.9, 0.49, 0.13),  # #e67e22
            borderPadding=(0, 0, 2, 0)
        )
        result['divider_color'] = colors.Color(0.83, 0.33, 0)  # #d35400

    elif template == 'minimal':
        result['name'] = ParagraphStyle(
            'Name',
            parent=styles['Title'],
            fontSize=14,
            textColor=colors.Color(0.2, 0.2, 0.2),  # #333
            alignment=TA_CENTER,
            letterSpacing=1
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
            letterSpacing=0.5,
            borderWidth=1,
            borderColor=colors.Color(0.87, 0.87, 0.87),  # #ddd
            borderPadding=(0, 0, 2, 0)
        )
        result['normal'] = ParagraphStyle(
            'Normal',
            parent=styles['Normal'],
            fontSize=9
        )
        result['list_item'] = ParagraphStyle(
            'ListItem',
            parent=styles['Normal'],
            fontSize=9
        )
        result['divider_color'] = colors.Color(0.87, 0.87, 0.87)  # #ddd

    elif template == 'executive':
        result['name'] = ParagraphStyle(
            'Name',
            parent=styles['Title'],
            fontSize=18,
            textColor=colors.Color(0.1, 0.1, 0.1),  # #1a1a1a
            alignment=TA_CENTER,
            textTransform='uppercase',
            borderWidth=3,
            borderColor=colors.Color(0.1, 0.1, 0.1),  # #1a1a1a
            borderPadding=(0, 0, 3, 0),
            borderStyle='double'
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
            borderWidth=1,
            borderColor=colors.Color(0.1, 0.1, 0.1),  # #1a1a1a
            borderPadding=(0, 0, 2, 0)
        )
        result['normal'] = ParagraphStyle(
            'Normal',
            parent=styles['Normal'],
            alignment=TA_JUSTIFY
        )
        result['divider_color'] = colors.Color(0.1, 0.1, 0.1)  # #1a1a1a

    else:
        # Default to professional if template not found
        return get_template_styles('professional')

    return result

