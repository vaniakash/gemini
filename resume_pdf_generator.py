from fpdf import FPDF
import os
from datetime import datetime

def generate_resume_pdf(resume_data):
    """Generate a PDF version of the resume"""
    pdf = FPDF()
    pdf.add_page()
    
    # Set up fonts
    pdf.set_font("Arial", "B", 16)
    
    # Personal Info
    if resume_data.get("personal_info"):
        pi = resume_data["personal_info"]
        if pi.get("Full Name"):
            pdf.cell(0, 10, pi.get("Full Name", "").upper(), 0, 1, "C")
        
        # Contact info
        pdf.set_font("Arial", "", 10)
        contact_info = []
        if pi.get('Email'): contact_info.append(f"Email: {pi['Email']}")
        if pi.get('Phone'): contact_info.append(f"Phone: {pi['Phone']}")
        if pi.get('LinkedIn (optional)'): contact_info.append(f"LinkedIn: {pi['LinkedIn (optional)']}")
        if pi.get('Portfolio/Website (optional)'): contact_info.append(f"Website: {pi['Portfolio/Website (optional)']}")
        
        if contact_info:
            pdf.cell(0, 6, " | ".join(contact_info), 0, 1, "C")
        
        pdf.ln(5)
    
    # Summary
    if resume_data.get("summary") and resume_data["summary"].get("Briefly describe your professional background and career objectives"):
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "PROFESSIONAL SUMMARY", 0, 1)
        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(0, 5, resume_data["summary"]["Briefly describe your professional background and career objectives"])
        pdf.ln(5)
    
    # Education
    if resume_data.get("education") and len(resume_data["education"]) > 0:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "EDUCATION", 0, 1)
        pdf.set_font("Arial", "", 10)
        
        for edu in resume_data["education"]:
            if edu.get("Degree") and edu.get("Institution"):
                pdf.set_font("Arial", "B", 10)
                pdf.cell(0, 6, f"{edu.get('Degree')} - {edu.get('Institution')}", 0, 1)
                pdf.set_font("Arial", "", 10)
                pdf.cell(0, 6, f"Graduation: {edu.get('Graduation Year', 'N/A')}", 0, 1)
                if edu.get('GPA (optional)'):
                    pdf.cell(0, 6, f"GPA: {edu.get('GPA (optional)')}", 0, 1)
                if edu.get('Relevant Coursework (optional)'):
                    pdf.cell(0, 6, f"Relevant Coursework: {edu.get('Relevant Coursework (optional)')}", 0, 1)
                pdf.ln(2)
        pdf.ln(3)
    
    # Experience
    if resume_data.get("experience") and len(resume_data["experience"]) > 0:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "WORK EXPERIENCE", 0, 1)
        
        for exp in resume_data["experience"]:
            if exp.get("Job Title") and exp.get("Company"):
                pdf.set_font("Arial", "B", 10)
                pdf.cell(0, 6, f"{exp.get('Job Title')} at {exp.get('Company')}", 0, 1)
                pdf.set_font("Arial", "", 10)
                pdf.cell(0, 6, f"{exp.get('Start Date (MM/YYYY)', 'N/A')} to {exp.get('End Date (MM/YYYY or \'Present\')', 'N/A')}", 0, 1)
                if exp.get('Description of responsibilities and achievements'):
                    pdf.ln(2)
                    pdf.multi_cell(0, 5, exp.get('Description of responsibilities and achievements'))
                pdf.ln(3)
        pdf.ln(2)
    
    # Skills
    if resume_data.get("skills"):
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "SKILLS", 0, 1)
        
        if resume_data["skills"].get("Technical skills (comma separated)"):
            pdf.set_font("Arial", "B", 10)
            pdf.cell(0, 6, "Technical Skills:", 0, 1)
            pdf.set_font("Arial", "", 10)
            
            tech_skills = resume_data["skills"]["Technical skills (comma separated)"].split(',')
            for skill in tech_skills:
                if skill.strip():
                    pdf.cell(0, 5, f"• {skill.strip()}", 0, 1)
        
        if resume_data["skills"].get("Soft skills (comma separated)"):
            pdf.ln(2)
            pdf.set_font("Arial", "B", 10)
            pdf.cell(0, 6, "Soft Skills:", 0, 1)
            pdf.set_font("Arial", "", 10)
            
            soft_skills = resume_data["skills"]["Soft skills (comma separated)"].split(',')
            for skill in soft_skills:
                if skill.strip():
                    pdf.cell(0, 5, f"• {skill.strip()}", 0, 1)
        pdf.ln(5)
    
    # Projects
    if resume_data.get("projects") and len(resume_data["projects"]) > 0:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "PROJECTS", 0, 1)
        
        for proj in resume_data["projects"]:
            if proj.get("Project Name"):
                pdf.set_font("Arial", "B", 10)
                pdf.cell(0, 6, f"{proj.get('Project Name')}", 0, 1)
                pdf.set_font("Arial", "", 10)
                
                if proj.get('Description'):
                    pdf.cell(0, 6, f"Description: {proj.get('Description')}", 0, 1)
                if proj.get('Technologies Used'):
                    pdf.cell(0, 6, f"Technologies Used: {proj.get('Technologies Used')}", 0, 1)
                if proj.get('URL (optional)'):
                    pdf.cell(0, 6, f"URL: {proj.get('URL (optional)')}", 0, 1)
                pdf.ln(3)
        pdf.ln(2)
    
    # Certifications
    if resume_data.get("certifications") and resume_data["certifications"].get("Certification Name"):
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "CERTIFICATIONS", 0, 1)
        
        cert = resume_data["certifications"]
        if cert.get("Certification Name"):
            pdf.set_font("Arial", "B", 10)
            pdf.cell(0, 6, f"{cert.get('Certification Name')}", 0, 1)
            pdf.set_font("Arial", "", 10)
            
            if cert.get('Issuing Organization'):
                pdf.cell(0, 6, f"Issuing Organization: {cert.get('Issuing Organization')}", 0, 1)
            if cert.get('Date Obtained (MM/YYYY)'):
                pdf.cell(0, 6, f"Date Obtained: {cert.get('Date Obtained (MM/YYYY)')}", 0, 1)
            if cert.get('Expiration Date (if applicable)'):
                pdf.cell(0, 6, f"Expiration Date: {cert.get('Expiration Date (if applicable)')}", 0, 1)
    
    # Create resumes directory if it doesn't exist
    if not os.path.exists("resumes"):
        os.makedirs("resumes")
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name = "resume"
    if resume_data.get("personal_info") and resume_data["personal_info"].get("Full Name"):
        name = resume_data["personal_info"]["Full Name"].replace(" ", "_").lower()
    
    filename = f"resumes/{name}_{timestamp}.pdf"
    pdf.output(filename)
    
    return filename 