from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import os
import uuid
import re
import html

def generate_pdf(html_content, template):
    """
    Generate a PDF from HTML content using the selected template with ReportLab.

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

        # Convert HTML to a format ReportLab can use
        content = convert_html_to_reportlab(html_content, template)

        # Create the PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )

        # Build the PDF
        doc.build(content)

        return output_path

    except Exception as e:
        raise Exception(f"Error generating PDF: {str(e)}")

def convert_html_to_reportlab(html_content, template):
    """
    Convert HTML content to ReportLab elements.

    Args:
        html_content (str): HTML content
        template (str): Template name

    Returns:
        list: List of ReportLab elements
    """
    # Get styles based on template
    styles = get_template_styles(template)

    # Clean up HTML content
    html_content = html_content.replace('<br>', '\n')

    # Extract content from HTML
    elements = []

    # Simple HTML parsing (for a real app, use a proper HTML parser)
    # Extract h1 tags (name/title)
    h1_matches = re.findall(r'<h1[^>]*>(.*?)</h1>', html_content, re.DOTALL)
    for match in h1_matches:
        text = html.unescape(match.strip())
        elements.append(Paragraph(text, styles['h1']))
        elements.append(Spacer(1, 12))

    # Extract h2 tags (section headers)
    h2_matches = re.findall(r'<h2[^>]*>(.*?)</h2>', html_content, re.DOTALL)
    for match in h2_matches:
        text = html.unescape(match.strip())
        elements.append(Paragraph(text, styles['h2']))
        elements.append(Spacer(1, 8))

    # Extract p tags (paragraphs)
    p_matches = re.findall(r'<p[^>]*>(.*?)</p>', html_content, re.DOTALL)
    for match in p_matches:
        text = html.unescape(match.strip())
        elements.append(Paragraph(text, styles['normal']))
        elements.append(Spacer(1, 6))

    # Extract ul/li tags (lists)
    ul_matches = re.findall(r'<ul[^>]*>(.*?)</ul>', html_content, re.DOTALL)
    for ul in ul_matches:
        li_matches = re.findall(r'<li[^>]*>(.*?)</li>', ul, re.DOTALL)
        for match in li_matches:
            text = html.unescape(match.strip())
            elements.append(Paragraph(f"• {text}", styles['bullet']))
            elements.append(Spacer(1, 3))
        elements.append(Spacer(1, 6))

    # If no elements were extracted, use the raw content
    if not elements:
        # Remove all HTML tags and use the plain text
        plain_text = re.sub(r'<[^>]*>', '', html_content)
        plain_text = html.unescape(plain_text.strip())
        elements.append(Paragraph(plain_text, styles['normal']))

    return elements

def get_template_styles(template):
    """
    Get the ReportLab styles for the selected template.

    Args:
        template (str): Template name

    Returns:
        dict: Dictionary of styles
    """
    # Get base styles
    styles = getSampleStyleSheet()

    # Template-specific styles
    if template == 'professional':
        h1_style = ParagraphStyle(
            'Professional H1',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=6,
            borderWidth=1,
            borderColor=colors.HexColor('#3498db'),
            borderPadding=5,
            borderRadius=2,
            alignment=TA_CENTER
        )

        h2_style = ParagraphStyle(
            'Professional H2',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2980b9'),
            spaceAfter=4
        )

        normal_style = ParagraphStyle(
            'Professional Normal',
            parent=styles['Normal'],
            fontSize=11,
            leading=14
        )

        bullet_style = ParagraphStyle(
            'Professional Bullet',
            parent=styles['Normal'],
            fontSize=11,
            leading=14,
            leftIndent=20
        )

    elif template == 'creative':
        h1_style = ParagraphStyle(
            'Creative H1',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#8e44ad'),
            spaceAfter=8,
            alignment=TA_CENTER
        )

        h2_style = ParagraphStyle(
            'Creative H2',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#d35400'),
            spaceAfter=6
        )

        normal_style = ParagraphStyle(
            'Creative Normal',
            parent=styles['Normal'],
            fontSize=11,
            leading=15
        )

        bullet_style = ParagraphStyle(
            'Creative Bullet',
            parent=styles['Normal'],
            fontSize=11,
            leading=15,
            leftIndent=20
        )

    elif template == 'minimal':
        h1_style = ParagraphStyle(
            'Minimal H1',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.black,
            spaceAfter=6,
            alignment=TA_CENTER
        )

        h2_style = ParagraphStyle(
            'Minimal H2',
            parent=styles['Heading2'],
            fontSize=13,
            textColor=colors.gray,
            spaceAfter=4
        )

        normal_style = ParagraphStyle(
            'Minimal Normal',
            parent=styles['Normal'],
            fontSize=10,
            leading=13
        )

        bullet_style = ParagraphStyle(
            'Minimal Bullet',
            parent=styles['Normal'],
            fontSize=10,
            leading=13,
            leftIndent=15
        )

    elif template == 'executive':
        h1_style = ParagraphStyle(
            'Executive H1',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.black,
            spaceAfter=10,
            borderWidth=0,
            borderColor=colors.black,
            borderPadding=0,
            alignment=TA_CENTER
        )

        h2_style = ParagraphStyle(
            'Executive H2',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.black,
            spaceAfter=6
        )

        normal_style = ParagraphStyle(
            'Executive Normal',
            parent=styles['Normal'],
            fontSize=11,
            leading=14,
            fontName='Times-Roman'
        )

        bullet_style = ParagraphStyle(
            'Executive Bullet',
            parent=styles['Normal'],
            fontSize=11,
            leading=14,
            leftIndent=20,
            fontName='Times-Roman'
        )

    else:
        # Default to professional if template not found
        return get_template_styles('professional')

    return {
        'h1': h1_style,
        'h2': h2_style,
        'normal': normal_style,
        'bullet': bullet_style
    }

