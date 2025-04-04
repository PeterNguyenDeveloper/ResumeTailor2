from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.units import inch
import os
import uuid
import re
import html
import traceback

def generate_pdf(html_content, template):
    """
    Generate a PDF from HTML content using ReportLab with enhanced formatting.

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

        # Save the HTML content for debugging
        debug_html_path = os.path.join(output_dir, f"debug_{uuid.uuid4()}.html")
        with open(debug_html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        # Extract structured content from HTML
        structured_content = extract_structured_content(html_content)

        # Create the PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            leftMargin=0.75*inch,
            rightMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )

        # Get styles based on the template
        styles = get_template_styles(template)

        # Build the PDF content
        elements = []

        # Add name (h1)
        if structured_content.get('name'):
            elements.append(Paragraph(structured_content['name'], styles['name']))
            elements.append(Spacer(1, 0.1*inch))

        # Add contact info
        if structured_content.get('contact_info'):
            elements.append(Paragraph(structured_content['contact_info'], styles['contact_info']))
            elements.append(Spacer(1, 0.3*inch))

        # Add sections
        for section in structured_content.get('sections', []):
            # Add section heading
            if section.get('heading'):
                elements.append(Paragraph(section['heading'], styles['heading']))
                elements.append(Spacer(1, 0.1*inch))

            # Add section content
            for content_item in section.get('content', []):
                if content_item['type'] == 'paragraph':
                    elements.append(Paragraph(content_item['text'], styles['normal']))
                    elements.append(Spacer(1, 0.1*inch))

                elif content_item['type'] == 'list':
                    items = []
                    for item_text in content_item['items']:
                        items.append(ListItem(Paragraph(item_text, styles['list_item'])))

                    if items:
                        elements.append(ListFlowable(
                            items,
                            bulletType='bullet',
                            leftIndent=0.25*inch,
                            bulletFontSize=10,
                            bulletOffsetY=2
                        ))
                        elements.append(Spacer(1, 0.1*inch))

                elif content_item['type'] == 'experience':
                    # Format experience items with better layout
                    for exp in content_item['items']:
                        # Title and company/date on the same line with different alignments
                        if exp.get('title') and exp.get('company'):
                            title_company = Table(
                                [[
                                    Paragraph(exp['title'], styles['exp_title']),
                                    Paragraph(exp['company'], styles['exp_company'])
                                ]],
                                colWidths=[doc.width*0.6, doc.width*0.4],
                                style=TableStyle([
                                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                    ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                                    ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                                    ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                                    ('TOPPADDING', (0, 0), (-1, -1), 2),
                                ])
                            )
                            elements.append(title_company)

                        # Location and date
                        if exp.get('location') or exp.get('date'):
                            location_date = ""
                            if exp.get('location') and exp.get('date'):
                                location_date = f"{exp['location']} | {exp['date']}"
                            elif exp.get('location'):
                                location_date = exp['location']
                            elif exp.get('date'):
                                location_date = exp['date']

                            if location_date:
                                elements.append(Paragraph(location_date, styles['exp_details']))
                                elements.append(Spacer(1, 0.05*inch))

                        # Description
                        if exp.get('description'):
                            elements.append(Paragraph(exp['description'], styles['normal']))

                        # Responsibilities/achievements as bullet points
                        if exp.get('bullets'):
                            items = []
                            for bullet in exp['bullets']:
                                items.append(ListItem(Paragraph(bullet, styles['list_item'])))

                            if items:
                                elements.append(Spacer(1, 0.05*inch))
                                elements.append(ListFlowable(
                                    items,
                                    bulletType='bullet',
                                    leftIndent=0.25*inch,
                                    bulletFontSize=10,
                                    bulletOffsetY=2
                                ))

                        elements.append(Spacer(1, 0.15*inch))

                elif content_item['type'] == 'education':
                    # Format education items with better layout
                    for edu in content_item['items']:
                        # Degree and institution/date on the same line with different alignments
                        if edu.get('degree') and edu.get('institution'):
                            degree_institution = Table(
                                [[
                                    Paragraph(edu['degree'], styles['edu_degree']),
                                    Paragraph(edu['institution'], styles['edu_institution'])
                                ]],
                                colWidths=[doc.width*0.6, doc.width*0.4],
                                style=TableStyle([
                                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                    ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                                    ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                                    ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                                    ('TOPPADDING', (0, 0), (-1, -1), 2),
                                ])
                            )
                            elements.append(degree_institution)

                        # Location and date
                        if edu.get('location') or edu.get('date'):
                            location_date = ""
                            if edu.get('location') and edu.get('date'):
                                location_date = f"{edu['location']} | {edu['date']}"
                            elif edu.get('location'):
                                location_date = edu['location']
                            elif edu.get('date'):
                                location_date = edu['date']

                            if location_date:
                                elements.append(Paragraph(location_date, styles['edu_details']))

                        # Additional details
                        if edu.get('details'):
                            elements.append(Spacer(1, 0.05*inch))
                            elements.append(Paragraph(edu['details'], styles['normal']))

                        elements.append(Spacer(1, 0.15*inch))

                elif content_item['type'] == 'skills':
                    # Format skills with better layout
                    skill_groups = content_item.get('groups', [])
                    for group in skill_groups:
                        if group.get('title'):
                            elements.append(Paragraph(group['title'], styles['skill_category']))

                        if group.get('skills'):
                            elements.append(Paragraph(group['skills'], styles['skill_list']))
                            elements.append(Spacer(1, 0.1*inch))

            # Add spacer after section
            elements.append(Spacer(1, 0.2*inch))

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

def extract_structured_content(html_content):
    """
    Extract structured content from HTML for enhanced PDF formatting.

    Args:
        html_content (str): HTML content

    Returns:
        dict: Structured data for PDF generation
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
            result['name'] = clean_text_for_reportlab(name_match.group(1))

        # Extract contact info
        contact_match = re.search(r'<p class="contact-info">(.*?)</p>', html_content, re.DOTALL | re.IGNORECASE)
        if contact_match:
            result['contact_info'] = clean_text_for_reportlab(contact_match.group(1))

        # Extract sections
        section_pattern = r'<div class="section">(.*?)</div>'
        section_matches = re.finditer(section_pattern, html_content, re.DOTALL | re.IGNORECASE)

        for section_match in section_matches:
            section_content = section_match.group(1)
            section = {
                'heading': '',
                'content': []
            }

            # Extract section heading
            heading_match = re.search(r'<h2>(.*?)</h2>', section_content, re.DOTALL | re.IGNORECASE)
            if heading_match:
                section['heading'] = clean_text_for_reportlab(heading_match.group(1))

            # Check if this is an Experience section
            if section['heading'] and ('experience' in section['heading'].lower() or 'work' in section['heading'].lower()):
                # Try to extract structured experience items
                experience_items = extract_experience_items(section_content)
                if experience_items:
                    section['content'].append({
                        'type': 'experience',
                        'items': experience_items
                    })
                else:
                    # Fall back to regular paragraph and list extraction
                    extract_paragraphs_and_lists(section_content, section)

            # Check if this is an Education section
            elif section['heading'] and 'education' in section['heading'].lower():
                # Try to extract structured education items
                education_items = extract_education_items(section_content)
                if education_items:
                    section['content'].append({
                        'type': 'education',
                        'items': education_items
                    })
                else:
                    # Fall back to regular paragraph and list extraction
                    extract_paragraphs_and_lists(section_content, section)

            # Check if this is a Skills section
            elif section['heading'] and 'skill' in section['heading'].lower():
                # Try to extract structured skills
                skill_groups = extract_skills(section_content)
                if skill_groups:
                    section['content'].append({
                        'type': 'skills',
                        'groups': skill_groups
                    })
                else:
                    # Fall back to regular paragraph and list extraction
                    extract_paragraphs_and_lists(section_content, section)

            # For other sections, extract paragraphs and lists
            else:
                extract_paragraphs_and_lists(section_content, section)

            if section['heading'] or section['content']:
                result['sections'].append(section)

    except Exception as e:
        # If there's an error in parsing, create a simple section with the error
        result['sections'] = [{
            'heading': 'Resume Content',
            'content': [{
                'type': 'paragraph',
                'text': 'There was an error parsing the resume HTML. Please try again.'
            }]
        }]

    return result

def extract_paragraphs_and_lists(section_content, section):
    """
    Extract paragraphs and lists from section content.

    Args:
        section_content (str): HTML content of the section
        section (dict): Section dictionary to update
    """
    # Extract paragraphs (excluding contact-info paragraphs)
    paragraph_pattern = r'<p(?!\s+class="contact-info")[^>]*>(.*?)</p>'
    paragraph_matches = re.finditer(paragraph_pattern, section_content, re.DOTALL | re.IGNORECASE)

    for paragraph_match in paragraph_matches:
        paragraph_text = paragraph_match.group(1).strip()
        clean_text = clean_text_for_reportlab(paragraph_text)
        if clean_text:
            section['content'].append({
                'type': 'paragraph',
                'text': clean_text
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
            item_text = item_match.group(1).strip()
            clean_text = clean_text_for_reportlab(item_text)
            if clean_text:
                list_items.append(clean_text)

        if list_items:
            section['content'].append({
                'type': 'list',
                'items': list_items
            })

def extract_experience_items(section_content):
    """
    Extract structured experience items from the section content.

    Args:
        section_content (str): HTML content of the section

    Returns:
        list: List of experience items
    """
    experience_items = []

    # Remove the section heading
    section_content = re.sub(r'<h2>.*?</h2>', '', section_content, flags=re.DOTALL | re.IGNORECASE)

    # Try to find experience entries (could be in various formats)
    # Look for patterns like:
    # <p><strong>Job Title</strong> at <strong>Company</strong>, Location | Date</p>
    # <p><strong>Job Title</strong>, <strong>Company</strong>, Location, Date</p>

    # First, try to find entries with strong tags
    exp_entries = re.finditer(r'<p>(?:.*?<strong>(.*?)</strong>.*?(?:<strong>(.*?)</strong>)?.*?)</p>',
                             section_content, re.DOTALL | re.IGNORECASE)

    for entry in exp_entries:
        full_entry = entry.group(0)

        # Extract job title (first strong tag)
        title = clean_text_for_reportlab(entry.group(1)) if entry.group(1) else ""

        # Extract company (second strong tag if exists)
        company = clean_text_for_reportlab(entry.group(2)) if entry.group(2) else ""

        # If no company found but there's a title, try to extract company from the text
        if title and not company:
            company_match = re.search(r'at\s+(.*?)(?:,|\||\(|$)', full_entry, re.IGNORECASE)
            if company_match:
                company = clean_text_for_reportlab(company_match.group(1))

        # Extract location and date
        location = ""
        date = ""

        # Look for location
        location_match = re.search(r'(?:,|\|)\s*([^,|]+(?:City|Town|Village|County|State|Province|Country|Region))',
                                  full_entry, re.IGNORECASE)
        if location_match:
            location = clean_text_for_reportlab(location_match.group(1))

        # Look for date
        date_match = re.search(r'(?:,|\|)\s*(\d{4}\s*(?:-|–|to)\s*(?:\d{4}|Present|Current))',
                              full_entry, re.IGNORECASE)
        if date_match:
            date = clean_text_for_reportlab(date_match.group(1))

        # Extract description and bullets
        description = ""
        bullets = []

        # Find the next paragraph after this entry
        next_p_start = section_content.find('</p>', entry.end()) + 4
        next_entry_start = section_content.find('<p><strong>', next_p_start)
        if next_entry_start == -1:
            next_entry_start = len(section_content)

        # Extract content between this entry and the next
        entry_content = section_content[next_p_start:next_entry_start].strip()

        # Look for description paragraph
        desc_match = re.search(r'<p>(.*?)</p>', entry_content, re.DOTALL | re.IGNORECASE)
        if desc_match:
            description = clean_text_for_reportlab(desc_match.group(1))

        # Look for bullet points
        bullet_list_match = re.search(r'<ul>(.*?)</ul>', entry_content, re.DOTALL | re.IGNORECASE)
        if bullet_list_match:
            bullet_items = re.finditer(r'<li>(.*?)</li>', bullet_list_match.group(1), re.DOTALL | re.IGNORECASE)
            for bullet in bullet_items:
                clean_bullet = clean_text_for_reportlab(bullet.group(1))
                if clean_bullet:
                    bullets.append(clean_bullet)

        # Create experience item
        if title or company:
            experience_items.append({
                'title': title,
                'company': company,
                'location': location,
                'date': date,
                'description': description,
                'bullets': bullets
            })

    return experience_items

def extract_education_items(section_content):
    """
    Extract structured education items from the section content.

    Args:
        section_content (str): HTML content of the section

    Returns:
        list: List of education items
    """
    education_items = []

    # Remove the section heading
    section_content = re.sub(r'<h2>.*?</h2>', '', section_content, flags=re.DOTALL | re.IGNORECASE)

    # Try to find education entries
    # Look for patterns like:
    # <p><strong>Degree</strong>, <strong>Institution</strong>, Location, Date</p>

    # First, try to find entries with strong tags
    edu_entries = re.finditer(r'<p>(?:.*?<strong>(.*?)</strong>.*?(?:<strong>(.*?)</strong>)?.*?)</p>',
                             section_content, re.DOTALL | re.IGNORECASE)

    for entry in edu_entries:
        full_entry = entry.group(0)

        # Extract degree (first strong tag)
        degree = clean_text_for_reportlab(entry.group(1)) if entry.group(1) else ""

        # Extract institution (second strong tag if exists)
        institution = clean_text_for_reportlab(entry.group(2)) if entry.group(2) else ""

        # If no institution found but there's a degree, try to extract institution from the text
        if degree and not institution:
            inst_match = re.search(r'at\s+(.*?)(?:,|\||\(|$)', full_entry, re.IGNORECASE)
            if inst_match:
                institution = clean_text_for_reportlab(inst_match.group(1))

        # Extract location and date
        location = ""
        date = ""

        # Look for location
        location_match = re.search(r'(?:,|\|)\s*([^,|]+(?:City|Town|Village|County|State|Province|Country|Region))',
                                  full_entry, re.IGNORECASE)
        if location_match:
            location = clean_text_for_reportlab(location_match.group(1))

        # Look for date
        date_match = re.search(r'(?:,|\|)\s*(\d{4}\s*(?:-|–|to)\s*(?:\d{4}|Present|Current))',
                              full_entry, re.IGNORECASE)
        if date_match:
            date = clean_text_for_reportlab(date_match.group(1))

        # Extract additional details
        details = ""

        # Find the next paragraph after this entry
        next_p_start = section_content.find('</p>', entry.end()) + 4
        next_entry_start = section_content.find('<p><strong>', next_p_start)
        if next_entry_start == -1:
            next_entry_start = len(section_content)

        # Extract content between this entry and the next
        entry_content = section_content[next_p_start:next_entry_start].strip()

        # Look for details paragraph
        details_match = re.search(r'<p>(.*?)</p>', entry_content, re.DOTALL | re.IGNORECASE)
        if details_match:
            details = clean_text_for_reportlab(details_match.group(1))

        # Create education item
        if degree or institution:
            education_items.append({
                'degree': degree,
                'institution': institution,
                'location': location,
                'date': date,
                'details': details
            })

    return education_items

def extract_skills(section_content):
    """
    Extract structured skills from the section content.

    Args:
        section_content (str): HTML content of the section

    Returns:
        list: List of skill groups
    """
    skill_groups = []

    # Remove the section heading
    section_content = re.sub(r'<h2>.*?</h2>', '', section_content, flags=re.DOTALL | re.IGNORECASE)

    # Try to find skill categories with strong tags
    skill_categories = re.finditer(r'<p>(?:<strong>(.*?)</strong>:?\s*(.*?))</p>',
                                  section_content, re.DOTALL | re.IGNORECASE)

    for category in skill_categories:
        title = clean_text_for_reportlab(category.group(1)) if category.group(1) else ""
        skills = clean_text_for_reportlab(category.group(2)) if category.group(2) else ""

        if title or skills:
            skill_groups.append({
                'title': title,
                'skills': skills
            })

    # If no structured skills found, try to extract from lists
    if not skill_groups:
        list_match = re.search(r'<ul>(.*?)</ul>', section_content, re.DOTALL | re.IGNORECASE)
        if list_match:
            list_content = list_match.group(1)
            skills_list = []

            item_matches = re.finditer(r'<li>(.*?)</li>', list_content, re.DOTALL | re.IGNORECASE)
            for item in item_matches:
                clean_skill = clean_text_for_reportlab(item.group(1))
                if clean_skill:
                    skills_list.append(clean_skill)

            if skills_list:
                skill_groups.append({
                    'title': 'Skills',
                    'skills': ', '.join(skills_list)
                })

    # If still no skills found, try to extract from paragraphs
    if not skill_groups:
        paragraph_match = re.search(r'<p>(.*?)</p>', section_content, re.DOTALL | re.IGNORECASE)
        if paragraph_match:
            skills_text = clean_text_for_reportlab(paragraph_match.group(1))
            if skills_text:
                skill_groups.append({
                    'title': '',
                    'skills': skills_text
                })

    return skill_groups

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
        ),
        'exp_title': ParagraphStyle(
            'ExpTitle',
            parent=styles['Normal'],
            fontSize=11,
            leading=14,
            fontName='Helvetica-Bold'
        ),
        'exp_company': ParagraphStyle(
            'ExpCompany',
            parent=styles['Normal'],
            fontSize=11,
            leading=14,
            alignment=TA_RIGHT
        ),
        'exp_details': ParagraphStyle(
            'ExpDetails',
            parent=styles['Normal'],
            fontSize=9,
            leading=12,
            textColor=colors.gray
        ),
        'edu_degree': ParagraphStyle(
            'EduDegree',
            parent=styles['Normal'],
            fontSize=11,
            leading=14,
            fontName='Helvetica-Bold'
        ),
        'edu_institution': ParagraphStyle(
            'EduInstitution',
            parent=styles['Normal'],
            fontSize=11,
            leading=14,
            alignment=TA_RIGHT
        ),
        'edu_details': ParagraphStyle(
            'EduDetails',
            parent=styles['Normal'],
            fontSize=9,
            leading=12,
            textColor=colors.gray
        ),
        'skill_category': ParagraphStyle(
            'SkillCategory',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            fontName='Helvetica-Bold'
        ),
        'skill_list': ParagraphStyle(
            'SkillList',
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
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            spaceAfter=6
        )
        result['contact_info'] = ParagraphStyle(
            'ContactInfo',
            parent=styles['Normal'],
            fontSize=9,
            alignment=TA_CENTER,
            textColor=colors.Color(0.33, 0.33, 0.33)
        )
        result['heading'] = ParagraphStyle(
            'Heading',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.Color(0.16, 0.5, 0.73),  # #2980b9
            fontName='Helvetica-Bold',
            borderWidth=0,
            borderPadding=0,
            borderColor=colors.Color(0.2, 0.6, 0.86)  # #3498db
        )
        result['exp_title']['textColor'] = colors.Color(0.16, 0.5, 0.73)  # #2980b9
        result['edu_degree']['textColor'] = colors.Color(0.16, 0.5, 0.73)  # #2980b9
        result['skill_category']['textColor'] = colors.Color(0.16, 0.5, 0.73)  # #2980b9

    elif template == 'creative':
        result['name'] = ParagraphStyle(
            'Name',
            parent=styles['Title'],
            fontSize=18,
            textColor=colors.Color(0.55, 0.27, 0.68),  # #8e44ad
            alignment=TA_CENTER,
            fontName='Times-Bold',
            spaceAfter=6
        )
        result['contact_info'] = ParagraphStyle(
            'ContactInfo',
            parent=styles['Normal'],
            fontSize=9,
            alignment=TA_CENTER,
            textColor=colors.Color(0.33, 0.33, 0.33)
        )
        result['heading'] = ParagraphStyle(
            'Heading',
            parent=styles['Heading2'],
            fontSize=13,
            textColor=colors.Color(0.83, 0.33, 0),  # #d35400
            fontName='Times-Bold',
            borderWidth=0,
            borderPadding=0,
            borderColor=colors.Color(0.9, 0.49, 0.13)  # #e67e22
        )
        result['exp_title']['textColor'] = colors.Color(0.83, 0.33, 0)  # #d35400
        result['edu_degree']['textColor'] = colors.Color(0.83, 0.33, 0)  # #d35400
        result['skill_category']['textColor'] = colors.Color(0.83, 0.33, 0)  # #d35400

    elif template == 'minimal':
        result['name'] = ParagraphStyle(
            'Name',
            parent=styles['Title'],
            fontSize=14,
            textColor=colors.Color(0.2, 0.2, 0.2),  # #333
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            spaceAfter=6
        )
        result['contact_info'] = ParagraphStyle(
            'ContactInfo',
            parent=styles['Normal'],
            fontSize=9,
            alignment=TA_CENTER,
            textColor=colors.Color(0.4, 0.4, 0.4)
        )
        result['heading'] = ParagraphStyle(
            'Heading',
            parent=styles['Heading2'],
            fontSize=11,
            textColor=colors.Color(0.33, 0.33, 0.33),  # #555
            fontName='Helvetica-Bold',
            borderWidth=0,
            borderPadding=0,
            borderColor=colors.Color(0.87, 0.87, 0.87)  # #ddd
        )
        result['normal'] = ParagraphStyle(
            'Normal',
            parent=styles['Normal'],
            fontSize=9,
            leading=12
        )
        result['exp_title']['fontSize'] = 10
        result['exp_company']['fontSize'] = 10
        result['edu_degree']['fontSize'] = 10
        result['edu_institution']['fontSize'] = 10
        result['skill_category']['fontSize'] = 10
        result['skill_list']['fontSize'] = 9

    elif template == 'executive':
        result['name'] = ParagraphStyle(
            'Name',
            parent=styles['Title'],
            fontSize=18,
            textColor=colors.Color(0.1, 0.1, 0.1),  # #1a1a1a
            alignment=TA_CENTER,
            fontName='Times-Bold',
            spaceAfter=6
        )
        result['contact_info'] = ParagraphStyle(
            'ContactInfo',
            parent=styles['Normal'],
            fontSize=9,
            alignment=TA_CENTER,
            textColor=colors.Color(0.2, 0.2, 0.2)
        )
        result['heading'] = ParagraphStyle(
            'Heading',
            parent=styles['Heading2'],
            fontSize=13,
            textColor=colors.Color(0.1, 0.1, 0.1),  # #1a1a1a
            fontName='Times-Bold',
            borderWidth=0,
            borderPadding=0,
            borderColor=colors.Color(0.1, 0.1, 0.1)  # #1a1a1a
        )
        result['normal'] = ParagraphStyle(
            'Normal',
            parent=styles['Normal'],
            alignment=TA_JUSTIFY
        )
        result['exp_title']['fontName'] = 'Times-Bold'
        result['exp_company']['fontName'] = 'Times-Roman'
        result['edu_degree']['fontName'] = 'Times-Bold'
        result['edu_institution']['fontName'] = 'Times-Roman'
        result['skill_category']['fontName'] = 'Times-Bold'
        result['skill_list']['fontName'] = 'Times-Roman'

    else:
        # Default to professional if template not found
        return get_template_styles('professional')

    return result

