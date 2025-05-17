from fpdf import FPDF
import os
from datetime import datetime
import re

class ResumePDF(FPDF):
    def __init__(self):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.add_page()
        self.set_auto_page_break(auto=True, margin=15)
        # Using the built-in Helvetica font which has better Unicode support
        self.set_font("Helvetica", size=12)
        self.line_height = 7  # Default line height

    def add_header(self, text, font_size=16, style='B'):
        self.set_font("Helvetica", style=style, size=font_size)
        self.cell(0, 10, self.sanitize_text(text), ln=True)
        self.set_font("Helvetica", size=12)  # Reset to normal font
        self.ln(2)

    def add_subheader(self, text, font_size=14, style='B'):
        self.set_font("Helvetica", style=style, size=font_size)
        self.cell(0, 8, self.sanitize_text(text), ln=True)
        self.set_font("Helvetica", size=12)  # Reset to normal font
        self.ln(1)

    def add_section_line(self):
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def add_text(self, text, font_size=12, style=''):
        self.set_font("Helvetica", style=style, size=font_size)
        self.multi_cell(0, self.line_height, self.sanitize_text(text))
        self.ln(2)

    def add_bullet_point(self, text, font_size=12):
        self.set_font("Helvetica", size=font_size)
        # Use a hyphen instead of bullet point for better compatibility
        self.cell(5, self.line_height, "-", 0, 0)
        self.multi_cell(0, self.line_height, self.sanitize_text(text))

    def add_contact_info_line(self, text_items):
        self.set_font("Helvetica", size=11)
        full_text = " | ".join(text_items)
        self.multi_cell(0, self.line_height, self.sanitize_text(full_text), align='C')
        self.ln(2)
        
    def sanitize_text(self, text):
        """Replace problematic characters with safe alternatives"""
        if text is None:
            return ""
        # Replace bullet points with hyphens
        text = text.replace('•', '-')
        # Replace other problematic Unicode characters if needed
        # Remove or replace characters that might cause encoding issues
        return text

def generate_resume_pdf(resume_data):
    """Generate a PDF resume from the resume data."""
    pdf = ResumePDF()
    
    # Personal Information
    if resume_data.get("personal_info"):
        pi = resume_data["personal_info"]
        if pi.get('Full Name'):
            pdf.add_header(pi.get('Full Name', '').upper(), font_size=18, style='B')
        
        contact_info = []
        if pi.get('Email'): contact_info.append(f"Email: {pi['Email']}")
        if pi.get('Phone'): contact_info.append(f"Phone: {pi['Phone']}")
        if pi.get('LinkedIn (optional)'): contact_info.append(f"LinkedIn: {pi['LinkedIn (optional)']}")
        if pi.get('Portfolio/Website (optional)'): contact_info.append(f"Website: {pi['Portfolio/Website (optional)']}")
        
        if contact_info:
            pdf.add_contact_info_line(contact_info)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(5)
    
    # Professional Summary
    if resume_data.get("summary") and resume_data["summary"].get("Briefly describe your professional background and career objectives"):
        pdf.add_subheader("PROFESSIONAL SUMMARY", font_size=14)
        pdf.add_section_line()
        pdf.add_text(resume_data["summary"]["Briefly describe your professional background and career objectives"])
        pdf.ln(5)
    
    # Education
    if resume_data.get("education") and len(resume_data["education"]) > 0:
        pdf.add_subheader("EDUCATION", font_size=14)
        pdf.add_section_line()
        
        for edu in resume_data["education"]:
            if edu.get("Degree") and edu.get("Institution"):
                pdf.add_text(f"{edu.get('Degree')} - {edu.get('Institution')}", style='B')
                pdf.add_text(f"Graduation: {edu.get('Graduation Year', 'N/A')}")
                if edu.get('GPA (optional)'):
                    pdf.add_text(f"GPA: {edu.get('GPA (optional)')}")
                if edu.get('Relevant Coursework (optional)'):
                    pdf.add_text(f"Relevant Coursework: {edu.get('Relevant Coursework (optional)')}")
                pdf.ln(3)
        pdf.ln(2)
    
    # Experience
    if resume_data.get("experience") and len(resume_data["experience"]) > 0:
        pdf.add_subheader("WORK EXPERIENCE", font_size=14)
        pdf.add_section_line()
        
        for exp in resume_data["experience"]:
            if exp.get("Job Title") and exp.get("Company"):
                pdf.add_text(f"{exp.get('Job Title')} at {exp.get('Company')}", style='B')
                pdf.add_text(f"{exp.get('Start Date (MM/YYYY)', 'N/A')} to {exp.get('End Date (MM/YYYY or \'Present\')', 'N/A')}")
                if exp.get('Description of responsibilities and achievements'):
                    pdf.add_text(exp.get('Description of responsibilities and achievements'))
                pdf.ln(3)
        pdf.ln(2)
    
    # Skills
    if resume_data.get("skills"):
        pdf.add_subheader("SKILLS", font_size=14)
        pdf.add_section_line()
        
        if resume_data["skills"].get("Technical skills (comma separated)"):
            tech_skills = resume_data["skills"]["Technical skills (comma separated)"].split(',')
            pdf.add_text("Technical Skills:", style='B')
            for skill in tech_skills:
                if skill.strip():
                    pdf.add_bullet_point(skill.strip())
            pdf.ln(3)
        
        if resume_data["skills"].get("Soft skills (comma separated)"):
            soft_skills = resume_data["skills"]["Soft skills (comma separated)"].split(',')
            pdf.add_text("Soft Skills:", style='B')
            for skill in soft_skills:
                if skill.strip():
                    pdf.add_bullet_point(skill.strip())
            pdf.ln(3)
        pdf.ln(2)
    
    # Projects
    if resume_data.get("projects") and len(resume_data["projects"]) > 0:
        pdf.add_subheader("PROJECTS", font_size=14)
        pdf.add_section_line()
        
        for proj in resume_data["projects"]:
            if proj.get("Project Name"):
                pdf.add_text(proj.get("Project Name"), style='B')
                if proj.get('Description'):
                    pdf.add_text(f"Description: {proj.get('Description')}")
                if proj.get('Technologies Used'):
                    pdf.add_text(f"Technologies Used: {proj.get('Technologies Used')}")
                if proj.get('URL (optional)'):
                    pdf.add_text(f"URL: {proj.get('URL (optional)')}")
                pdf.ln(3)
        pdf.ln(2)
    
    # Certifications
    if resume_data.get("certifications") and resume_data["certifications"].get("Certification Name"):
        pdf.add_subheader("CERTIFICATIONS", font_size=14)
        pdf.add_section_line()
        
        cert = resume_data["certifications"]
        if cert.get("Certification Name"):
            pdf.add_text(cert.get("Certification Name"), style='B')
            if cert.get('Issuing Organization'):
                pdf.add_text(f"Issuing Organization: {cert.get('Issuing Organization')}")
            if cert.get('Date Obtained (MM/YYYY)'):
                pdf.add_text(f"Date Obtained: {cert.get('Date Obtained (MM/YYYY)')}")
            if cert.get('Expiration Date (if applicable)'):
                pdf.add_text(f"Expiration Date: {cert.get('Expiration Date (if applicable)')}")
    
    # Create resumes directory if it doesn't exist
    if not os.path.exists("resumes"):
        os.makedirs("resumes")
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name = "resume"
    if resume_data.get("personal_info") and resume_data["personal_info"].get("Full Name"):
        name = resume_data["personal_info"]["Full Name"].replace(" ", "_").lower()
    
    pdf_filename = f"resumes/{name}_{timestamp}.pdf"
    
    # Save the PDF
    pdf.output(pdf_filename)
    
    return pdf_filename 