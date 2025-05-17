import streamlit as st
from io import BytesIO
import os
from fpdf import FPDF
from pdf2image import convert_from_bytes
from PIL import Image
from resume_pdf_generator import generate_resume_pdf

def generate_resume_html_preview(resume_data):
    """Generate an HTML preview of the resume for display in Streamlit."""
    html = f"""
    <style>
        .resume-container {{
            font-family: Arial, sans-serif;
            max-width: 100%;
            margin: 0 auto;
            padding: 10px;
            border: 1px solid #ddd;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            background-color: white;
        }}
        .header {{
            text-align: center;
            margin-bottom: 15px;
        }}
        .name {{
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 5px;
            text-transform: uppercase;
        }}
        .contact-info {{
            font-size: 12px;
            color: #444;
            margin-bottom: 10px;
        }}
        .section {{
            margin-bottom: 15px;
        }}
        .section-header {{
            font-size: 16px;
            font-weight: bold;
            border-bottom: 1px solid #333;
            margin-bottom: 8px;
            padding-bottom: 3px;
            text-transform: uppercase;
        }}
        .entry {{
            margin-bottom: 10px;
        }}
        .entry-title {{
            font-weight: bold;
        }}
        .entry-subtitle {{
            font-style: italic;
        }}
        .bullet-list {{
            margin-left: 20px;
            list-style-type: disc;
        }}
    </style>
    <div class="resume-container">
    """
    
    # Personal Information
    if resume_data.get("personal_info"):
        pi = resume_data["personal_info"]
        html += '<div class="header">'
        if pi.get('Full Name'):
            html += f'<div class="name">{pi.get("Full Name", "")}</div>'
        
        contact_items = []
        if pi.get('Email'): contact_items.append(f"Email: {pi['Email']}")
        if pi.get('Phone'): contact_items.append(f"Phone: {pi['Phone']}")
        if pi.get('LinkedIn (optional)'): contact_items.append(f"LinkedIn: {pi['LinkedIn (optional)']}")
        if pi.get('Portfolio/Website (optional)'): contact_items.append(f"Website: {pi['Portfolio/Website (optional)']}")
        
        if contact_items:
            html += f'<div class="contact-info">{" | ".join(contact_items)}</div>'
        html += '</div>'
    
    # Professional Summary
    if resume_data.get("summary") and resume_data["summary"].get("Briefly describe your professional background and career objectives"):
        html += '<div class="section">'
        html += '<div class="section-header">Professional Summary</div>'
        html += f'<p>{resume_data["summary"]["Briefly describe your professional background and career objectives"]}</p>'
        html += '</div>'
    
    # Education
    if resume_data.get("education") and len(resume_data["education"]) > 0:
        html += '<div class="section">'
        html += '<div class="section-header">Education</div>'
        
        for edu in resume_data["education"]:
            if edu.get("Degree") and edu.get("Institution"):
                html += '<div class="entry">'
                html += f'<div class="entry-title">{edu.get("Degree")} - {edu.get("Institution")}</div>'
                html += f'<div class="entry-subtitle">Graduation: {edu.get("Graduation Year", "N/A")}</div>'
                
                if edu.get('GPA (optional)'):
                    html += f'<div>GPA: {edu.get("GPA (optional)")}</div>'
                if edu.get('Relevant Coursework (optional)'):
                    html += f'<div>Relevant Coursework: {edu.get("Relevant Coursework (optional)")}</div>'
                html += '</div>'
        html += '</div>'
    
    # Experience
    if resume_data.get("experience") and len(resume_data["experience"]) > 0:
        html += '<div class="section">'
        html += '<div class="section-header">Work Experience</div>'
        
        for exp in resume_data["experience"]:
            if exp.get("Job Title") and exp.get("Company"):
                html += '<div class="entry">'
                html += f'<div class="entry-title">{exp.get("Job Title")} at {exp.get("Company")}</div>'
                html += f'<div class="entry-subtitle">{exp.get("Start Date (MM/YYYY)", "N/A")} to {exp.get("End Date (MM/YYYY or \'Present\')", "N/A")}</div>'
                
                if exp.get('Description of responsibilities and achievements'):
                    html += f'<p>{exp.get("Description of responsibilities and achievements")}</p>'
                html += '</div>'
        html += '</div>'
    
    # Skills
    if resume_data.get("skills"):
        html += '<div class="section">'
        html += '<div class="section-header">Skills</div>'
        
        if resume_data["skills"].get("Technical skills (comma separated)"):
            tech_skills = resume_data["skills"]["Technical skills (comma separated)"].split(',')
            html += '<div class="entry">'
            html += '<div class="entry-title">Technical Skills:</div>'
            html += '<ul class="bullet-list">'
            for skill in tech_skills:
                if skill.strip():
                    html += f'<li>{skill.strip()}</li>'
            html += '</ul>'
            html += '</div>'
        
        if resume_data["skills"].get("Soft skills (comma separated)"):
            soft_skills = resume_data["skills"]["Soft skills (comma separated)"].split(',')
            html += '<div class="entry">'
            html += '<div class="entry-title">Soft Skills:</div>'
            html += '<ul class="bullet-list">'
            for skill in soft_skills:
                if skill.strip():
                    html += f'<li>{skill.strip()}</li>'
            html += '</ul>'
            html += '</div>'
        html += '</div>'
    
    # Projects
    if resume_data.get("projects") and len(resume_data["projects"]) > 0:
        html += '<div class="section">'
        html += '<div class="section-header">Projects</div>'
        
        for proj in resume_data["projects"]:
            if proj.get("Project Name"):
                html += '<div class="entry">'
                html += f'<div class="entry-title">{proj.get("Project Name")}</div>'
                
                if proj.get('Description'):
                    html += f'<p>Description: {proj.get("Description")}</p>'
                if proj.get('Technologies Used'):
                    html += f'<p>Technologies Used: {proj.get("Technologies Used")}</p>'
                if proj.get('URL (optional)'):
                    html += f'<p>URL: {proj.get("URL (optional)")}</p>'
                html += '</div>'
        html += '</div>'
    
    # Certifications
    if resume_data.get("certifications") and resume_data["certifications"].get("Certification Name"):
        html += '<div class="section">'
        html += '<div class="section-header">Certifications</div>'
        
        cert = resume_data["certifications"]
        if cert.get("Certification Name"):
            html += '<div class="entry">'
            html += f'<div class="entry-title">{cert.get("Certification Name")}</div>'
            
            if cert.get('Issuing Organization'):
                html += f'<div>Issuing Organization: {cert.get("Issuing Organization")}</div>'
            if cert.get('Date Obtained (MM/YYYY)'):
                html += f'<div>Date Obtained: {cert.get("Date Obtained (MM/YYYY)")}</div>'
            if cert.get('Expiration Date (if applicable)'):
                html += f'<div>Expiration Date: {cert.get("Expiration Date (if applicable)")}</div>'
            html += '</div>'
        html += '</div>'
    
    html += '</div>'
    
    return html

def generate_resume_image(resume_data):
    """Generate a JPEG image of the resume using PDF conversion."""
    try:
        # First generate the PDF
        pdf_filename = generate_resume_pdf(resume_data)
        
        # Read the PDF file
        with open(pdf_filename, 'rb') as pdf_file:
            pdf_bytes = pdf_file.read()
        
        # Convert PDF to image
        images = convert_from_bytes(pdf_bytes, dpi=200)
        
        # Take the first page
        img = images[0]
        
        # Create an in-memory buffer for the image
        img_buffer = BytesIO()
        img.save(img_buffer, format='JPEG', quality=95)
        img_buffer.seek(0)
        
        return img_buffer
    except Exception as e:
        st.error(f"Error generating resume image: {str(e)}")
        return None 