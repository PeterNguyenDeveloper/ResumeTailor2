from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import uuid
import re
import html

# Register fonts if available
try:
    # Try to register some professional fonts
    pdfmetrics.registerFont(TTFont('Garamond', 'fonts/Garamond.ttf'))
    pdfmetrics.registerFont(TTFont('Garamond-Bold', 'fonts/Garamond-Bold.ttf'))
    pdfmetrics.registerFont(TTFont('Garamond-Italic', 'fonts/Garamond-Italic.ttf'))
    CUSTOM_FONTS_AVAILABLE = True
except:
    # If fonts aren't available, we'll use the default fonts
    CUSTOM_FONTS_AVAILABLE = False

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

        # Parse HTML and extract structured content
        resume_sections = parse_resume_html(html_content)

        # Convert to ReportLab elements with the selected template
        content = create_resume_document(resume_sections, template)

        # Create the PDF document with proper margins for a resume
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )

        # Build the PDF
        doc.build(content)

        return output_path

    except Exception as e:
        raise Exception(f"Error generating PDF: {str(e)}")

def parse_resume_html(html_content):
    """
    Parse HTML content and extract structured resume sections.

    Args:
        html_content (str): HTML content

    Returns:
        dict: Structured resume content
    """
    # Clean up HTML content
    html_content = html_content.replace('<br>', '\n')

    # Extract the name (usually the first h1)
    name = ""
    name_match = re.search(r'<h1[^>]*>(.*?)</h1>', html_content, re.DOTALL)
    if name_match:
        name = html.unescape(name_match.group(1).strip())
        # Remove the name from the content to avoid duplication
        html_content = html_content.replace(name_match.group(0), '', 1)

    # Extract contact info (usually a paragraph after the name)
    contact_info = ""
    contact_match = re.search(r'<p[^>]*>(.*?)</p>', html_content, re.DOTALL)
    if contact_match and len(contact_match.group(1).strip()) < 200:  # Assume contact info is short
        contact_info = html.unescape(contact_match.group(1).strip())
        # Remove the contact info from the content to avoid duplication
        html_content = html_content.replace(contact_match.group(0), '', 1)

    # Extract sections (h2 headers and their content)
    sections = []
    section_matches = re.finditer(r'<h2[^>]*>(.*?)</h2>', html_content, re.DOTALL)

    last_pos = 0
    for match in section_matches:
        section_title = html.unescape(match.group(1).strip())
        start_pos = match.end()

        # Find the next h2 tag or end of content
        next_match = re.search(r'<h2[^>]*>', html_content[start_pos:], re.DOTALL)
        if next_match:
            end_pos = start_pos + next_match.start()
            section_content = html_content[start_pos:end_pos]
        else:
            section_content = html_content[start_pos:]

        # Extract paragraphs and lists from the section content
        paragraphs = []
        p_matches = re.finditer(r'<p[^>]*>(.*?)</p>', section_content, re.DOTALL)
        for p_match in p_matches:
            paragraphs.append(html.unescape(p_match.group(1).strip()))

        lists = []
        ul_matches = re.finditer(r'<ul[^>]*>(.*?)</ul>', section_content, re.DOTALL)
        for ul_match in ul_matches:
            list_items = []
            li_matches = re.finditer(r'<li[^>]*>(.*?)</li>', ul_match.group(1), re.DOTALL)
            for li_match in li_matches:
                list_items.append(html.unescape(li_match.group(1).strip()))
            lists.append(list_items)

        sections.append({
            'title': section_title,
            'paragraphs': paragraphs,
            'lists': lists
        })

        last_pos = end_pos if next_match else len(html_content)

    # If no sections were found, extract all paragraphs and lists
    if not sections:
        paragraphs = []
        p_matches = re.finditer(r'<p[^>]*>(.*?)</p>', html_content, re.DOTALL)
        for p_match in p_matches:
            paragraphs.append(html.unescape(p_match.group(1).strip()))

        lists = []
        ul_matches = re.finditer(r'<ul[^>]*>(.*?)</ul>', html_content, re.DOTALL)
        for ul_match in ul_matches:
            list_items = []
            li_matches = re.finditer(r'<li[^>]*>(.*?)</li>', ul_match.group(1), re.DOTALL)
            for li_match in li_matches:
                list_items.append(html.unescape(li_match.group(1).strip()))
            lists.append(list_items)

        if paragraphs or lists:
            sections.append({
                'title': 'Resume',
                'paragraphs': paragraphs,
                'lists': lists
            })

    return {
        'name': name,
        'contact_info': contact_info,
        'sections': sections
    }

def create_resume_document(resume_data, template):
    """
    Create a ReportLab document from structured resume data.

    Args:
        resume_data (dict): Structured resume data
        template (str): Template name

    Returns:
        list: List of ReportLab elements
    """
    # Get styles based on template
    styles = get_template_styles(template)

    elements = []

    # Add name
    if resume_data['name']:
        elements.append(Paragraph(resume_data['name'], styles['name']))
        elements.append(Spacer(1, 0.1*inch))

    # Add contact info
    if resume_data['contact_info']:
        elements.append(Paragraph(resume_data['contact_info'], styles['contact']))
        elements.append(Spacer(1, 0.2*inch))

    # Add a divider line
    elements.append(HRFlowable(
        width="100%",
        thickness=1,
        color=styles['divider_color'],
        spaceBefore=0.1*inch,
        spaceAfter=0.2*inch
    ))

    # Add sections
    for section in resume_data['sections']:
        # Create a section that stays together
        section_elements = []

        # Add section title
        section_elements.append(Paragraph(section['title'], styles['section_title']))
        section_elements.append(Spacer(1, 0.1*inch))

        # Add paragraphs
        for paragraph in section['paragraphs']:
            section_elements.append(Paragraph(paragraph, styles['normal']))
            section_elements.append(Spacer(1, 0.1*inch))

        # Add lists
        for list_items in section['lists']:
            for item in list_items:
                section_elements.append(Paragraph(f"• {item}", styles['bullet']))
                section_elements.append(Spacer(1, 0.05*inch))
            section_elements.append(Spacer(1, 0.05*inch))

        # Add a divider after each section (except the last one)
        if section != resume_data['sections'][-1]:
            section_elements.append(HRFlowable(
                width="100%",
                thickness=1,
                color=styles['divider_color'],
                spaceBefore=0.1*inch,
                spaceAfter=0.2*inch,
                lineCap='round'
            ))

        # Keep the section together if possible
        elements.append(KeepTogether(section_elements))

    return elements

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

    # Define font family based on availability
    if CUSTOM_FONTS_AVAILABLE:
        base_font = 'Garamond'
        base_font_bold = 'Garamond-Bold'
        base_font_italic = 'Garamond-Italic'
    else:
        base_font = 'Times-Roman'
        base_font_bold = 'Times-Bold'
        base_font_italic = 'Times-Italic'

    # Template-specific styles
    if template == 'professional':
        name_style = ParagraphStyle(
            'Professional Name',
            fontName=base_font_bold,
            fontSize=16,
            textColor=colors.HexColor('#2c3e50'),
            alignment=TA_CENTER,
            spaceAfter=6
        )

        contact_style = ParagraphStyle(
            'Professional Contact',
            fontName=base_font,
            fontSize=10,
            textColor=colors.HexColor('#2c3e50'),
            alignment=TA_CENTER,
            spaceAfter=6
        )

        section_title_style = ParagraphStyle(
            'Professional Section Title',
            fontName=base_font_bold,
            fontSize=12,
            textColor=colors.HexColor('#2980b9'),
            spaceAfter=6
        )

        normal_style = ParagraphStyle(
            'Professional Normal',
            fontName=base_font,
            fontSize=10,
            leading=14,
            alignment=TA_JUSTIFY
        )

        bullet_style = ParagraphStyle(
            'Professional Bullet',
            fontName=base_font,
            fontSize=10,
            leading=14,
            leftIndent=20,
            alignment=TA_JUSTIFY
        )

        divider_color = colors.HexColor('#3498db')

    elif template == 'creative':
        name_style = ParagraphStyle(
            'Creative Name',
            fontName=base_font_bold,
            fontSize=18,
            textColor=colors.HexColor('#8e44ad'),
            alignment=TA_CENTER,
            spaceAfter=8
        )

        contact_style = ParagraphStyle(
            'Creative Contact',
            fontName=base_font_italic,
            fontSize=10,
            textColor=colors.HexColor('#8e44ad'),
            alignment=TA_CENTER,
            spaceAfter=8
        )

        section_title_style = ParagraphStyle(
            'Creative Section Title',
            fontName=base_font_bold,
            fontSize=14,
            textColor=colors.HexColor('#d35400'),
            spaceAfter=8
        )

        normal_style = ParagraphStyle(
            'Creative Normal',
            fontName=base_font,
            fontSize=10,
            leading=15,
            alignment=TA_JUSTIFY
        )

        bullet_style = ParagraphStyle(
            'Creative Bullet',
            fontName=base_font,
            fontSize=10,
            leading=15,
            leftIndent=20,
            alignment=TA_JUSTIFY
        )

        divider_color = colors.HexColor('#d35400')

    elif template == 'minimal':
        name_style = ParagraphStyle(
            'Minimal Name',
            fontName=base_font_bold,
            fontSize=16,
            textColor=colors.black,
            alignment=TA_CENTER,
            spaceAfter=6
        )

        contact_style = ParagraphStyle(
            'Minimal Contact',
            fontName=base_font,
            fontSize=9,
            textColor=colors.gray,
            alignment=TA_CENTER,
            spaceAfter=6
        )

        section_title_style = ParagraphStyle(
            'Minimal Section Title',
            fontName=base_font_bold,
            fontSize=11,
            textColor=colors.black,
            spaceAfter=4
        )

        normal_style = ParagraphStyle(
            'Minimal Normal',
            fontName=base_font,
            fontSize=9,
            leading=13,
            alignment=TA_JUSTIFY
        )

        bullet_style = ParagraphStyle(
            'Minimal Bullet',
            fontName=base_font,
            fontSize=9,
            leading=13,
            leftIndent=15,
            alignment=TA_JUSTIFY
        )

        divider_color = colors.gray

    elif template == 'executive':
        name_style = ParagraphStyle(
            'Executive Name',
            fontName=base_font_bold,
            fontSize=18,
            textColor=colors.black,
            alignment=TA_CENTER,
            spaceAfter=10
        )

        contact_style = ParagraphStyle(
            'Executive Contact',
            fontName=base_font,
            fontSize=10,
            textColor=colors.black,
            alignment=TA_CENTER,
            spaceAfter=10
        )

        section_title_style = ParagraphStyle(
            'Executive Section Title',
            fontName=base_font_bold,
            fontSize=12,
            textColor=colors.black,
            spaceAfter=8
        )

        normal_style = ParagraphStyle(
            'Executive Normal',
            fontName=base_font,
            fontSize=10,
            leading=14,
            alignment=TA_JUSTIFY
        )

        bullet_style = ParagraphStyle(
            'Executive Bullet',
            fontName=base_font,
            fontSize=10,
            leading=14,
            leftIndent=20,
            alignment=TA_JUSTIFY
        )

        divider_color = colors.black

    else:
        # Default to professional if template not found
        return get_template_styles('professional')

    return {
        'name': name_style,
        'contact': contact_style,
        'section_title': section_title_style,
        'normal': normal_style,
        'bullet': bullet_style,
        'divider_color': divider_color
    }

