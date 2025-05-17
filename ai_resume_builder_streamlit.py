import streamlit as st
import google.generativeai as genai
import json
import os
import time
from datetime import datetime
from fpdf import FPDF
from resume_pdf_generator import generate_resume_pdf
from resume_previewer import generate_resume_html_preview, generate_resume_image

# Configure the Gemini API
API_KEY = "AIzaSyCGh5_4qhlwDgQ3V05tzH2ztdD3efbaUM8"
genai.configure(api_key=API_KEY)

# Initialize the model - using flash model for higher quota limits
model = genai.GenerativeModel('models/gemini-1.5-flash')

# Resume sections and questions
RESUME_SECTIONS = {
    "personal_info": [
        "Full Name",
        "Email",
        "Phone",
        "LinkedIn (optional)",
        "Portfolio/Website (optional)"
    ],
    "summary": [
        "Briefly describe your professional background and career objectives"
    ],
    "education": [
        "Degree",
        "Institution",
        "Graduation Year",
        "GPA (optional)",
        "Relevant Coursework (optional)"
    ],
    "experience": [
        "Job Title",
        "Company",
        "Start Date (MM/YYYY)",
        "End Date (MM/YYYY or 'Present')",
        "Description of responsibilities and achievements"
    ],
    "skills": [
        "Technical skills (comma separated)",
        "Soft skills (comma separated)"
    ],
    "projects": [
        "Project Name",
        "Description",
        "Technologies Used",
        "URL (optional)"
    ],
    "certifications": [
        "Certification Name",
        "Issuing Organization",
        "Date Obtained (MM/YYYY)",
        "Expiration Date (if applicable)"
    ]
}

# Initialize session state
def init_session_state():
    if 'resume_data' not in st.session_state:
        st.session_state.resume_data = {section: {} for section in RESUME_SECTIONS}
        for section in ["education", "experience", "projects"]:
            st.session_state.resume_data[section] = []
    
    if 'current_section' not in st.session_state:
        st.session_state.current_section = "personal_info"
    
    if 'feedback' not in st.session_state:
        st.session_state.feedback = ""

def get_ai_feedback(section_name, content):
    """Get AI feedback on a resume section."""
    try:
        with st.spinner('Getting AI feedback...'):
            prompt = f"""
            As a resume expert, review this {section_name} section of a resume and provide specific, actionable feedback:
            
            {content}
            
            Provide 3 brief, specific suggestions to improve this section. Make them concise, direct, and immediately actionable.
            Format your response as:
            1. [First suggestion]
            2. [Second suggestion]
            3. [Third suggestion]
            """
            
            response = model.generate_content(prompt)
            return response.text
    except Exception as e:
        if "429" in str(e):
            return "⚠️ API rate limit reached. Please try again in a few minutes."
        return f"⚠️ Could not get AI feedback: {str(e)}"

def generate_ai_summary():
    """Generate an AI summary of the entire resume and provide overall feedback."""
    try:
        with st.spinner('Analyzing your complete resume...'):
            resume_text = json.dumps(st.session_state.resume_data, indent=2)
            
            prompt = f"""
            As a resume expert, review this entire resume:
            
            {resume_text}
            
            Provide 5 specific recommendations to improve this resume overall. Focus on content, structure, and impact.
            Then provide a brief assessment of the resume's strengths.
            
            Format your response as:
            
            IMPROVEMENT RECOMMENDATIONS:
            1. [First recommendation]
            2. [Second recommendation]
            3. [Third recommendation]
            4. [Fourth recommendation]
            5. [Fifth recommendation]
            
            STRENGTHS:
            - [List 3 strengths of this resume]
            """
            
            response = model.generate_content(prompt)
            return response.text
    except Exception as e:
        if "429" in str(e):
            return "⚠️ API rate limit reached. Please try again in a few minutes."
        return f"⚠️ Could not get AI feedback: {str(e)}"

def generate_formatted_resume(resume_data):
    """Convert resume data to a properly formatted text resume."""
    formatted_text = []
    
    # Personal Information
    if resume_data.get("personal_info"):
        pi = resume_data["personal_info"]
        formatted_text.append("=" * 60)
        formatted_text.append(f"{pi.get('Full Name', '').upper()}")
        contact_info = []
        if pi.get('Email'): contact_info.append(f"Email: {pi['Email']}")
        if pi.get('Phone'): contact_info.append(f"Phone: {pi['Phone']}")
        if pi.get('LinkedIn (optional)'): contact_info.append(f"LinkedIn: {pi['LinkedIn (optional)']}")
        if pi.get('Portfolio/Website (optional)'): contact_info.append(f"Website: {pi['Portfolio/Website (optional)']}")
        formatted_text.append(' | '.join(contact_info))
        formatted_text.append("=" * 60)
        formatted_text.append("")
    
    # Professional Summary
    if resume_data.get("summary") and resume_data["summary"].get("Briefly describe your professional background and career objectives"):
        formatted_text.append("PROFESSIONAL SUMMARY")
        formatted_text.append("-" * 60)
        formatted_text.append(resume_data["summary"]["Briefly describe your professional background and career objectives"])
        formatted_text.append("")
    
    # Education
    if resume_data.get("education") and len(resume_data["education"]) > 0:
        formatted_text.append("EDUCATION")
        formatted_text.append("-" * 60)
        for edu in resume_data["education"]:
            if edu.get("Degree") and edu.get("Institution"):
                formatted_text.append(f"{edu.get('Degree')} - {edu.get('Institution')}")
                formatted_text.append(f"Graduation: {edu.get('Graduation Year', 'N/A')}")
                if edu.get('GPA (optional)'):
                    formatted_text.append(f"GPA: {edu.get('GPA (optional)')}")
                if edu.get('Relevant Coursework (optional)'):
                    formatted_text.append(f"Relevant Coursework: {edu.get('Relevant Coursework (optional)')}")
                formatted_text.append("")
        formatted_text.append("")
    
    # Experience
    if resume_data.get("experience") and len(resume_data["experience"]) > 0:
        formatted_text.append("WORK EXPERIENCE")
        formatted_text.append("-" * 60)
        for exp in resume_data["experience"]:
            if exp.get("Job Title") and exp.get("Company"):
                formatted_text.append(f"{exp.get('Job Title')} at {exp.get('Company')}")
                formatted_text.append(f"{exp.get('Start Date (MM/YYYY)', 'N/A')} to {exp.get('End Date (MM/YYYY or \'Present\')', 'N/A')}")
                if exp.get('Description of responsibilities and achievements'):
                    formatted_text.append("")
                    formatted_text.append(exp.get('Description of responsibilities and achievements'))
                formatted_text.append("")
        formatted_text.append("")
    
    # Skills
    if resume_data.get("skills"):
        formatted_text.append("SKILLS")
        formatted_text.append("-" * 60)
        if resume_data["skills"].get("Technical skills (comma separated)"):
            tech_skills = resume_data["skills"]["Technical skills (comma separated)"].split(',')
            formatted_text.append("Technical Skills:")
            for skill in tech_skills:
                if skill.strip():
                    formatted_text.append(f"• {skill.strip()}")
        
        if resume_data["skills"].get("Soft skills (comma separated)"):
            soft_skills = resume_data["skills"]["Soft skills (comma separated)"].split(',')
            formatted_text.append("")
            formatted_text.append("Soft Skills:")
            for skill in soft_skills:
                if skill.strip():
                    formatted_text.append(f"• {skill.strip()}")
        formatted_text.append("")
    
    # Projects
    if resume_data.get("projects") and len(resume_data["projects"]) > 0:
        formatted_text.append("PROJECTS")
        formatted_text.append("-" * 60)
        for proj in resume_data["projects"]:
            if proj.get("Project Name"):
                formatted_text.append(f"{proj.get('Project Name')}")
                if proj.get('Description'):
                    formatted_text.append(f"Description: {proj.get('Description')}")
                if proj.get('Technologies Used'):
                    formatted_text.append(f"Technologies Used: {proj.get('Technologies Used')}")
                if proj.get('URL (optional)'):
                    formatted_text.append(f"URL: {proj.get('URL (optional)')}")
                formatted_text.append("")
        formatted_text.append("")
    
    # Certifications
    if resume_data.get("certifications") and resume_data["certifications"].get("Certification Name"):
        formatted_text.append("CERTIFICATIONS")
        formatted_text.append("-" * 60)
        cert = resume_data["certifications"]
        if cert.get("Certification Name"):
            formatted_text.append(f"{cert.get('Certification Name')}")
            if cert.get('Issuing Organization'):
                formatted_text.append(f"Issuing Organization: {cert.get('Issuing Organization')}")
            if cert.get('Date Obtained (MM/YYYY)'):
                formatted_text.append(f"Date Obtained: {cert.get('Date Obtained (MM/YYYY)')}")
            if cert.get('Expiration Date (if applicable)'):
                formatted_text.append(f"Expiration Date: {cert.get('Expiration Date (if applicable)')}")
    
    # Join all sections with proper spacing
    return "\n".join(formatted_text)

def save_resume():
    """Save the resume data to a JSON file."""
    try:
        # Create resumes directory if it doesn't exist
        if not os.path.exists("resumes"):
            os.makedirs("resumes")
            
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name = "resume"
        if st.session_state.resume_data.get("personal_info") and st.session_state.resume_data["personal_info"].get("Full Name"):
            name = st.session_state.resume_data["personal_info"]["Full Name"].replace(" ", "_").lower()
        
        filename = f"resumes/{name}_{timestamp}.json"
        
        # Save the data
        with open(filename, "w") as f:
            json.dump(st.session_state.resume_data, f, indent=2)
            
        st.success(f"Resume saved to {filename}")
        
        # Return the filename so we can offer it for download
        return filename
    except Exception as e:
        st.error(f"Error saving resume: {e}")
        return None

def render_personal_info():
    st.subheader("Personal Information")
    
    # Initialize if not present
    if not st.session_state.resume_data["personal_info"]:
        st.session_state.resume_data["personal_info"] = {q: "" for q in RESUME_SECTIONS["personal_info"]}
    
    # Create the form
    with st.form("personal_info_form"):
        form_data = {}
        for question in RESUME_SECTIONS["personal_info"]:
            current_value = st.session_state.resume_data["personal_info"].get(question, "")
            form_data[question] = st.text_input(question, value=current_value)
        
        submitted = st.form_submit_button("Save")
        
        if submitted:
            st.session_state.resume_data["personal_info"] = form_data
            st.success("Personal information saved!")
            st.rerun()  # Refresh to update the preview

def render_summary():
    st.subheader("Professional Summary")
    
    # Initialize if not present
    if not st.session_state.resume_data["summary"]:
        st.session_state.resume_data["summary"] = {q: "" for q in RESUME_SECTIONS["summary"]}
    
    # Create the form
    with st.form("summary_form"):
        form_data = {}
        for question in RESUME_SECTIONS["summary"]:
            current_value = st.session_state.resume_data["summary"].get(question, "")
            form_data[question] = st.text_area(question, value=current_value, height=150)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            submitted = st.form_submit_button("Save")
        with col2:
            get_feedback = st.form_submit_button("Save & Get AI Feedback")
        
        if submitted or get_feedback:
            st.session_state.resume_data["summary"] = form_data
            st.success("Summary saved!")
            
            if get_feedback:
                section_text = "\n".join([f"{k}: {v}" for k, v in form_data.items()])
                feedback = get_ai_feedback("summary", section_text)
                st.session_state.feedback = feedback

def render_skills():
    st.subheader("Skills")
    
    # Initialize if not present
    if not st.session_state.resume_data["skills"]:
        st.session_state.resume_data["skills"] = {q: "" for q in RESUME_SECTIONS["skills"]}
    
    # Create the form
    with st.form("skills_form"):
        form_data = {}
        for question in RESUME_SECTIONS["skills"]:
            current_value = st.session_state.resume_data["skills"].get(question, "")
            form_data[question] = st.text_area(question, value=current_value, height=100)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            submitted = st.form_submit_button("Save")
        with col2:
            get_feedback = st.form_submit_button("Save & Get AI Feedback")
        
        if submitted or get_feedback:
            st.session_state.resume_data["skills"] = form_data
            st.success("Skills saved!")
            
            if get_feedback:
                section_text = "\n".join([f"{k}: {v}" for k, v in form_data.items()])
                feedback = get_ai_feedback("skills", section_text)
                st.session_state.feedback = feedback

def render_certifications():
    st.subheader("Certifications")
    
    # Initialize if not present
    if not st.session_state.resume_data["certifications"]:
        st.session_state.resume_data["certifications"] = {q: "" for q in RESUME_SECTIONS["certifications"]}
    
    # Create the form
    with st.form("certifications_form"):
        form_data = {}
        for question in RESUME_SECTIONS["certifications"]:
            current_value = st.session_state.resume_data["certifications"].get(question, "")
            form_data[question] = st.text_input(question, value=current_value)
        
        submitted = st.form_submit_button("Save")
        
        if submitted:
            st.session_state.resume_data["certifications"] = form_data
            st.success("Certifications saved!")

def render_education():
    st.subheader("Education")
    
    # Show existing entries
    if st.session_state.resume_data["education"]:
        st.write("Existing Education Entries:")
        for i, entry in enumerate(st.session_state.resume_data["education"]):
            with st.expander(f"{entry.get('Degree', 'Education')} - {entry.get('Institution', '')}"):
                st.write(f"**Degree:** {entry.get('Degree', '')}")
                st.write(f"**Institution:** {entry.get('Institution', '')}")
                st.write(f"**Graduation Year:** {entry.get('Graduation Year', '')}")
                if entry.get('GPA (optional)', ''):
                    st.write(f"**GPA:** {entry.get('GPA (optional)', '')}")
                if entry.get('Relevant Coursework (optional)', ''):
                    st.write(f"**Relevant Coursework:** {entry.get('Relevant Coursework (optional)', '')}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"Edit #{i+1}", key=f"edit_edu_{i}"):
                        st.session_state.edit_education_index = i
                with col2:
                    if st.button(f"Delete #{i+1}", key=f"delete_edu_{i}"):
                        st.session_state.resume_data["education"].pop(i)
                        st.rerun()
    
    # Edit existing entry or add new one
    if hasattr(st.session_state, 'edit_education_index'):
        edit_index = st.session_state.edit_education_index
        st.subheader(f"Edit Education #{edit_index+1}")
        current_data = st.session_state.resume_data["education"][edit_index]
    else:
        st.subheader("Add New Education")
        current_data = {q: "" for q in RESUME_SECTIONS["education"]}
        edit_index = None
    
    # Education form
    with st.form("education_form"):
        form_data = {}
        for question in RESUME_SECTIONS["education"]:
            current_value = current_data.get(question, "")
            if question in ["Relevant Coursework (optional)"]:
                form_data[question] = st.text_area(question, value=current_value, height=100)
            else:
                form_data[question] = st.text_input(question, value=current_value)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            submitted = st.form_submit_button("Save")
        with col2:
            if edit_index is not None:
                cancel = st.form_submit_button("Cancel Edit")
            else:
                cancel = st.form_submit_button("Clear Form")
        with col3:
            if edit_index is None:  # Only for new entries
                get_feedback = st.form_submit_button("Save & Get AI Feedback")
            else:
                get_feedback = False
        
        if submitted or get_feedback:
            if edit_index is not None:
                st.session_state.resume_data["education"][edit_index] = form_data
                del st.session_state.edit_education_index
                st.success("Education entry updated!")
            else:
                st.session_state.resume_data["education"].append(form_data)
                st.success("New education entry added!")
            
            if get_feedback:
                section_text = "\n".join([f"{k}: {v}" for k, v in form_data.items()])
                feedback = get_ai_feedback("education", section_text)
                st.session_state.feedback = feedback
            
            st.rerun()
            
        if cancel:
            if hasattr(st.session_state, 'edit_education_index'):
                del st.session_state.edit_education_index
            st.rerun()

def render_experience():
    st.subheader("Work Experience")
    
    # Show existing entries
    if st.session_state.resume_data["experience"]:
        st.write("Existing Experience Entries:")
        for i, entry in enumerate(st.session_state.resume_data["experience"]):
            with st.expander(f"{entry.get('Job Title', 'Job')} at {entry.get('Company', '')}"):
                st.write(f"**Job Title:** {entry.get('Job Title', '')}")
                st.write(f"**Company:** {entry.get('Company', '')}")
                st.write(f"**Duration:** {entry.get('Start Date (MM/YYYY)', '')} to {entry.get('End Date (MM/YYYY or \'Present\')', '')}")
                st.write(f"**Description:** {entry.get('Description of responsibilities and achievements', '')}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"Edit #{i+1}", key=f"edit_exp_{i}"):
                        st.session_state.edit_experience_index = i
                with col2:
                    if st.button(f"Delete #{i+1}", key=f"delete_exp_{i}"):
                        st.session_state.resume_data["experience"].pop(i)
                        st.rerun()
    
    # Edit existing entry or add new one
    if hasattr(st.session_state, 'edit_experience_index'):
        edit_index = st.session_state.edit_experience_index
        st.subheader(f"Edit Experience #{edit_index+1}")
        current_data = st.session_state.resume_data["experience"][edit_index]
    else:
        st.subheader("Add New Experience")
        current_data = {q: "" for q in RESUME_SECTIONS["experience"]}
        edit_index = None
    
    # Experience form
    with st.form("experience_form"):
        form_data = {}
        for question in RESUME_SECTIONS["experience"]:
            current_value = current_data.get(question, "")
            if question == "Description of responsibilities and achievements":
                form_data[question] = st.text_area(question, value=current_value, height=150)
            else:
                form_data[question] = st.text_input(question, value=current_value)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            submitted = st.form_submit_button("Save")
        with col2:
            if edit_index is not None:
                cancel = st.form_submit_button("Cancel Edit")
            else:
                cancel = st.form_submit_button("Clear Form")
        with col3:
            if edit_index is None:  # Only for new entries
                get_feedback = st.form_submit_button("Save & Get AI Feedback")
            else:
                get_feedback = False
        
        if submitted or get_feedback:
            if edit_index is not None:
                st.session_state.resume_data["experience"][edit_index] = form_data
                del st.session_state.edit_experience_index
                st.success("Experience entry updated!")
            else:
                st.session_state.resume_data["experience"].append(form_data)
                st.success("New experience entry added!")
            
            if get_feedback:
                section_text = "\n".join([f"{k}: {v}" for k, v in form_data.items()])
                feedback = get_ai_feedback("experience", section_text)
                st.session_state.feedback = feedback
            
            st.rerun()
            
        if cancel:
            if hasattr(st.session_state, 'edit_experience_index'):
                del st.session_state.edit_experience_index
            st.rerun()

def render_projects():
    st.subheader("Projects")
    
    # Show existing entries
    if st.session_state.resume_data["projects"]:
        st.write("Existing Project Entries:")
        for i, entry in enumerate(st.session_state.resume_data["projects"]):
            with st.expander(f"{entry.get('Project Name', 'Project')}"):
                st.write(f"**Project Name:** {entry.get('Project Name', '')}")
                st.write(f"**Description:** {entry.get('Description', '')}")
                st.write(f"**Technologies Used:** {entry.get('Technologies Used', '')}")
                if entry.get('URL (optional)', ''):
                    st.write(f"**URL:** {entry.get('URL (optional)', '')}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"Edit #{i+1}", key=f"edit_proj_{i}"):
                        st.session_state.edit_project_index = i
                with col2:
                    if st.button(f"Delete #{i+1}", key=f"delete_proj_{i}"):
                        st.session_state.resume_data["projects"].pop(i)
                        st.rerun()
    
    # Edit existing entry or add new one
    if hasattr(st.session_state, 'edit_project_index'):
        edit_index = st.session_state.edit_project_index
        st.subheader(f"Edit Project #{edit_index+1}")
        current_data = st.session_state.resume_data["projects"][edit_index]
    else:
        st.subheader("Add New Project")
        current_data = {q: "" for q in RESUME_SECTIONS["projects"]}
        edit_index = None
    
    # Project form
    with st.form("project_form"):
        form_data = {}
        for question in RESUME_SECTIONS["projects"]:
            current_value = current_data.get(question, "")
            if question == "Description":
                form_data[question] = st.text_area(question, value=current_value, height=150)
            else:
                form_data[question] = st.text_input(question, value=current_value)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            submitted = st.form_submit_button("Save")
        with col2:
            if edit_index is not None:
                cancel = st.form_submit_button("Cancel Edit")
            else:
                cancel = st.form_submit_button("Clear Form")
        with col3:
            if edit_index is None:  # Only for new entries
                get_feedback = st.form_submit_button("Save & Get AI Feedback")
            else:
                get_feedback = False
        
        if submitted or get_feedback:
            if edit_index is not None:
                st.session_state.resume_data["projects"][edit_index] = form_data
                del st.session_state.edit_project_index
                st.success("Project entry updated!")
            else:
                st.session_state.resume_data["projects"].append(form_data)
                st.success("New project entry added!")
            
            if get_feedback:
                section_text = "\n".join([f"{k}: {v}" for k, v in form_data.items()])
                feedback = get_ai_feedback("project", section_text)
                st.session_state.feedback = feedback
            
            st.rerun()
            
        if cancel:
            if hasattr(st.session_state, 'edit_project_index'):
                del st.session_state.edit_project_index
            st.rerun()

def main():
    st.set_page_config(
        page_title="AI Resume Builder",
        page_icon="📝",
        layout="wide"
    )
    
    # Initialize session state
    init_session_state()
    
    # App header
    st.title("📝 AI Resume Builder")
    st.markdown("Build your professional resume with AI-powered guidance")
    
    # Main layout with sidebar
    with st.sidebar:
        st.header("Navigation")
        section = st.radio(
            "Select Resume Section:",
            ["Personal Info", "Summary", "Education", "Experience", "Skills", "Projects", "Certifications", "AI Report"]
        )
        
        # Save and export buttons
        st.header("Save & Export")
        if st.button("Save Resume"):
            if not st.session_state.resume_data.get("personal_info"):
                st.error("Please complete at least the Personal Info section before saving.")
            else:
                filename = save_resume()
                if filename:
                    with open(filename, 'r') as f:
                        file_content = f.read()
                    st.download_button(
                        label="Download Resume JSON",
                        data=file_content,
                        file_name=os.path.basename(filename),
                        mime="application/json"
                    )
        
        # Export as PDF file
        if st.button("Export as PDF"):
            if not st.session_state.resume_data.get("personal_info"):
                st.error("Please complete at least the Personal Info section before exporting.")
            else:
                try:
                    with st.spinner("Generating PDF..."):
                        pdf_filename = generate_resume_pdf(st.session_state.resume_data)
                    
                    st.success(f"PDF resume created: {pdf_filename}")
                    
                    with open(pdf_filename, 'rb') as f:
                        pdf_bytes = f.read()
                    
                    st.download_button(
                        label="Download Resume PDF",
                        data=pdf_bytes,
                        file_name=os.path.basename(pdf_filename),
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error(f"Error generating PDF: {str(e)}")
        
        # Download as text file
        if st.button("Export as Text File"):
            if not st.session_state.resume_data.get("personal_info"):
                st.error("Please complete at least the Personal Info section before exporting.")
            else:
                formatted_resume = generate_formatted_resume(st.session_state.resume_data)
                
                # Create filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                name = "resume"
                if st.session_state.resume_data.get("personal_info") and st.session_state.resume_data["personal_info"].get("Full Name"):
                    name = st.session_state.resume_data["personal_info"]["Full Name"].replace(" ", "_").lower()
                
                st.download_button(
                    label="Download Resume Text",
                    data=formatted_resume,
                    file_name=f"{name}_{timestamp}.txt",
                    mime="text/plain"
                )
                
                # Preview the formatted resume
                with st.expander("Preview Formatted Resume"):
                    st.text(formatted_resume)
    
    # Main layout (3 columns)
    left_col, middle_col, right_col = st.columns([2, 2, 1])
    
    # Resume form column
    with left_col:
        if section == "Personal Info":
            render_personal_info()
        elif section == "Summary":
            render_summary()
        elif section == "Education":
            render_education()
        elif section == "Experience":
            render_experience()
        elif section == "Skills":
            render_skills()
        elif section == "Projects":
            render_projects()
        elif section == "Certifications":
            render_certifications()
        elif section == "AI Report":
            st.subheader("AI Resume Analysis")
            
            # Check if we have data for all sections
            missing_sections = []
            for section in RESUME_SECTIONS:
                if not st.session_state.resume_data.get(section):
                    missing_sections.append(section.replace('_', ' ').title())
            
            if missing_sections:
                st.warning(f"Please complete these sections before generating a full report: {', '.join(missing_sections)}")
            else:
                if st.button("Generate AI Report"):
                    feedback = generate_ai_summary()
                    st.session_state.feedback = feedback
    
    # Live resume preview column
    with middle_col:
        st.subheader("Live Resume Preview")
        preview_html = generate_resume_html_preview(st.session_state.resume_data)
        st.components.v1.html(preview_html, height=600, scrolling=True)
        
        # Add "Export as JPEG" button in the preview column
        if st.button("Export as JPEG"):
            if not st.session_state.resume_data.get("personal_info"):
                st.error("Please complete at least the Personal Info section before exporting.")
            else:
                try:
                    with st.spinner("Generating JPEG..."):
                        img_buffer = generate_resume_image(st.session_state.resume_data)
                    
                    if img_buffer:
                        # Create filename with timestamp
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        name = "resume"
                        if st.session_state.resume_data.get("personal_info") and st.session_state.resume_data["personal_info"].get("Full Name"):
                            name = st.session_state.resume_data["personal_info"]["Full Name"].replace(" ", "_").lower()
                        
                        st.download_button(
                            label="Download Resume JPEG",
                            data=img_buffer,
                            file_name=f"{name}_{timestamp}.jpg",
                            mime="image/jpeg"
                        )
                except Exception as e:
                    st.error(f"Error generating JPEG: {str(e)}")
    
    # Feedback area
    with right_col:
        st.subheader("AI Feedback")
        if st.session_state.feedback:
            st.markdown(st.session_state.feedback)
        else:
            st.info("AI feedback will appear here. Use the 'Get AI Feedback' buttons to receive personalized suggestions for your resume content.")

if __name__ == "__main__":
    main() 