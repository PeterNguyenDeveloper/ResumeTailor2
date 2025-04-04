from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER
import os
import uuid
import re
import html

def generate_pdf(html_content, template):
    try:
        output_dir = 'generated_pdfs'
        os.makedirs(output_dir, exist_ok=True)

        output_path = os.path.join(output_dir, f"{uuid.uuid4()}_resume.pdf")
        content = convert_html_to_reportlab(html_content, template)

        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )

        doc.build(content)
        return output_path

    except Exception as e:
        raise Exception(f"Error generating PDF: {str(e)}")


def convert_html_to_reportlab(html_content, template):
    styles = get_template_styles(template)
    html_content = html_content.replace('<br>', '\n')
    elements = []

    h1_matches = re.findall(r'<h1[^>]*>(.*?)</h1>', html_content, re.DOTALL)
    for match in h1_matches:
        text = html.unescape(match.strip())
        elements.append(Paragraph(text, styles['h1']))
        elements.append(Spacer(1, 12))

    h2_matches = re.findall(r'<h2[^>]*>(.*?)</h2>', html_content, re.DOTALL)
    for match in h2_matches:
        text = html.unescape(match.strip())
        elements.append(Paragraph(text, styles['h2']))
        elements.append(Spacer(1, 8))

    p_matches = re.findall(r'<p[^>]*>(.*?)</p>', html_content, re.DOTALL)
    for match in p_matches:
        text = html.unescape(match.strip())
        elements.append(Paragraph(text, styles['normal']))
        elements.append(Spacer(1, 6))

    ul_matches = re.findall(r'<ul[^>]*>(.*?)</ul>', html_content, re.DOTALL)
    for ul in ul_matches:
        li_matches = re.findall(r'<li[^>]*>(.*?)</li>', ul, re.DOTALL)
        for match in li_matches:
            text = html.unescape(match.strip())
            elements.append(Paragraph(f"• {text}", styles['bullet']))
            elements.append(Spacer(1, 3))
        elements.append(Spacer(1, 6))

    if not elements:
        plain_text = re.sub(r'<[^>]*>', '', html_content)
        plain_text = html.unescape(plain_text.strip())
        elements.append(Paragraph(plain_text, styles['normal']))

    return elements


def get_template_styles(template):
    styles = getSampleStyleSheet()

    if template == 'professional':
        h1_style = ParagraphStyle(
            'Professional H1',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=6,
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
        return get_template_styles('professional')

    return {
        'h1': h1_style,
        'h2': h2_style,
        'normal': normal_style,
        'bullet': bullet_style
    }
