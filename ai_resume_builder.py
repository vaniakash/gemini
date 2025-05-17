import google.generativeai as genai
import json
import os
import time
from datetime import datetime

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
        "Briefly describe your professional background and career objectives (2-3 sentences)"
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
        "List your technical skills (comma separated)",
        "List your soft skills (comma separated)"
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

def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 50)
    print(f"📝 {text}")
    print("=" * 50)

def get_ai_feedback(section_name, content):
    """Get AI feedback on a resume section."""
    try:
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

def collect_section_data(section, questions):
    """Collect user data for a specific resume section."""
    print_header(f"{section.replace('_', ' ').title()} Section")
    
    if section == "experience" or section == "projects" or section == "education":
        entries = []
        while True:
            print(f"\nAdd a new {section[:-1]} entry:")
            entry = {}
            for question in questions:
                entry[question] = input(f"{question}: ")
            
            entries.append(entry)
            
            if input(f"\nAdd another {section[:-1]} entry? (y/n): ").lower() != 'y':
                break
                
        # Get AI feedback on the most recent entry
        if entries:
            latest_entry = entries[-1]
            entry_text = "\n".join([f"{k}: {v}" for k, v in latest_entry.items()])
            
            print("\n🤖 AI is analyzing your entry...")
            feedback = get_ai_feedback(section[:-1], entry_text)
            print(f"\n🤖 AI Suggestions for improvement:\n{feedback}")
            
        return entries
    else:
        data = {}
        for question in questions:
            data[question] = input(f"{question}: ")
            
        # For summary and skills, provide AI feedback
        if section in ["summary", "skills"]:
            section_text = "\n".join([f"{k}: {v}" for k, v in data.items()])
            
            print("\n🤖 AI is analyzing your entry...")
            feedback = get_ai_feedback(section, section_text)
            print(f"\n🤖 AI Suggestions for improvement:\n{feedback}")
            
            if input("\nWould you like to revise this section based on the AI feedback? (y/n): ").lower() == 'y':
                for question in questions:
                    data[question] = input(f"Revised {question}: ")
                    
        return data

def generate_ai_summary(resume_data):
    """Generate an AI summary of the entire resume and provide overall feedback."""
    try:
        resume_text = json.dumps(resume_data, indent=2)
        
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

def save_resume(resume_data):
    """Save the resume data to a JSON file."""
    if not os.path.exists("resumes"):
        os.makedirs("resumes")
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name = resume_data["personal_info"]["Full Name"].replace(" ", "_").lower()
    filename = f"resumes/{name}_{timestamp}.json"
    
    with open(filename, "w") as f:
        json.dump(resume_data, f, indent=2)
        
    print(f"\n✅ Resume saved to {filename}")
    return filename

def main():
    print_header("AI Resume Builder")
    print("This tool will guide you through creating a professional resume with AI assistance.")
    print("For each section, enter the requested information and receive AI feedback.")
    
    resume_data = {}
    
    # Collect data for each resume section
    for section, questions in RESUME_SECTIONS.items():
        resume_data[section] = collect_section_data(section, questions)
        
        # Skip AI feedback for personal info
        if section != "personal_info":
            time.sleep(1)  # Brief pause to avoid hitting API rate limits
    
    # Save the resume
    filename = save_resume(resume_data)
    
    # Generate overall AI feedback
    print("\n🤖 AI is analyzing your complete resume...")
    overall_feedback = generate_ai_summary(resume_data)
    print(f"\n🤖 AI Resume Assessment:\n{overall_feedback}")
    
    print("\n🎉 Your resume is complete! Use the AI feedback to make improvements.")
    print(f"Your resume data is saved at: {filename}")
    
if __name__ == "__main__":
    main() 