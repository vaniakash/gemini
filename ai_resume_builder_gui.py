import google.generativeai as genai
import json
import os
import time
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
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

class ResumeBuilderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Resume Builder")
        self.root.geometry("900x700")
        self.root.minsize(900, 700)
        
        # Set theme colors
        self.bg_color = "#f5f5f5"
        self.accent_color = "#4a6fa5"
        self.root.configure(bg=self.bg_color)
        
        # Styles
        self.style = ttk.Style()
        self.style.configure("TFrame", background=self.bg_color)
        self.style.configure("TButton", background=self.accent_color, foreground="white", font=("Arial", 11))
        self.style.configure("TLabel", background=self.bg_color, font=("Arial", 11))
        self.style.configure("Header.TLabel", font=("Arial", 16, "bold"))
        self.style.configure("Section.TLabel", font=("Arial", 14, "bold"))
        
        # Resume data store
        self.resume_data = {section: {} for section in RESUME_SECTIONS}
        self.current_section = "personal_info"
        self.section_entries = {}
        
        # Create main frames
        self.create_layout()
        
        # Start with the first section
        self.show_section("personal_info")
    
    def create_layout(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        header_label = ttk.Label(header_frame, text="AI Resume Builder", style="Header.TLabel")
        header_label.pack(side=tk.LEFT)
        
        # Content area (split into two parts)
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Navigation panel (left)
        nav_frame = ttk.Frame(content_frame, width=200, padding="10")
        nav_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        nav_label = ttk.Label(nav_frame, text="Resume Sections:", style="Section.TLabel")
        nav_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Create section buttons
        self.nav_buttons = {}
        for i, section in enumerate(RESUME_SECTIONS.keys()):
            display_name = section.replace('_', ' ').title()
            btn = ttk.Button(nav_frame, text=display_name, 
                             command=lambda s=section: self.show_section(s))
            btn.pack(fill=tk.X, pady=2)
            self.nav_buttons[section] = btn
        
        # Save button at the bottom of navigation
        ttk.Separator(nav_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        save_btn = ttk.Button(nav_frame, text="Save Resume", command=self.save_resume)
        save_btn.pack(fill=tk.X, pady=5)
        
        generate_report_btn = ttk.Button(nav_frame, text="Generate AI Report", 
                                         command=self.generate_ai_report)
        generate_report_btn.pack(fill=tk.X, pady=5)
        
        # Content panel (right)
        self.content_area = ttk.Frame(content_frame, padding="10")
        self.content_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Feedback area (bottom)
        self.feedback_frame = ttk.Frame(main_frame, padding="10")
        self.feedback_frame.pack(fill=tk.X, pady=(10, 0))
        
        feedback_label = ttk.Label(self.feedback_frame, text="AI Feedback:", style="Section.TLabel")
        feedback_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.feedback_text = scrolledtext.ScrolledText(self.feedback_frame, height=8, wrap=tk.WORD)
        self.feedback_text.pack(fill=tk.X)
        self.feedback_text.config(state=tk.DISABLED)
    
    def show_section(self, section_name):
        # Update selected button
        for section, btn in self.nav_buttons.items():
            btn.state(['!pressed'])
        self.nav_buttons[section_name].state(['pressed'])
        
        # Clear current content
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        # Update current section
        self.current_section = section_name
        display_name = section_name.replace('_', ' ').title()
        
        # Create section header
        section_label = ttk.Label(self.content_area, text=f"{display_name} Section", 
                                  style="Section.TLabel")
        section_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Special handling for multi-entry sections
        if section_name in ["education", "experience", "projects"]:
            self.create_multi_entry_section(section_name)
        else:
            self.create_single_entry_section(section_name)
    
    def create_single_entry_section(self, section_name):
        # Create form for single entry sections
        form_frame = ttk.Frame(self.content_area)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create entry fields for each question
        self.section_entries = {}
        
        for i, question in enumerate(RESUME_SECTIONS[section_name]):
            frame = ttk.Frame(form_frame)
            frame.pack(fill=tk.X, pady=5)
            
            label = ttk.Label(frame, text=f"{question}:")
            label.pack(anchor=tk.W)
            
            if "describe" in question.lower() or "responsibilities" in question.lower():
                # Use text area for longer text
                entry = scrolledtext.ScrolledText(frame, height=4, wrap=tk.WORD)
                if section_name in self.resume_data and question in self.resume_data[section_name]:
                    entry.insert(tk.END, self.resume_data[section_name][question])
            else:
                # Use single line entry for shorter text
                entry = ttk.Entry(frame, width=50)
                if section_name in self.resume_data and question in self.resume_data[section_name]:
                    entry.insert(0, self.resume_data[section_name][question])
            
            entry.pack(fill=tk.X)
            self.section_entries[question] = entry
        
        # Create buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        save_section_btn = ttk.Button(button_frame, text="Save Section", 
                                     command=self.save_section)
        save_section_btn.pack(side=tk.LEFT, padx=5)
        
        if section_name in ["summary", "skills"]:
            get_feedback_btn = ttk.Button(button_frame, text="Get AI Feedback", 
                                         command=self.get_section_feedback)
            get_feedback_btn.pack(side=tk.LEFT, padx=5)
    
    def create_multi_entry_section(self, section_name):
        # Container for this section
        container = ttk.Frame(self.content_area)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Create scrollable list of existing entries
        if section_name in self.resume_data and self.resume_data[section_name]:
            entries_frame = ttk.LabelFrame(container, text="Existing Entries")
            entries_frame.pack(fill=tk.X, pady=(0, 10))
            
            for i, entry in enumerate(self.resume_data[section_name]):
                entry_summary = f"{i+1}. "
                if section_name == "education":
                    entry_summary += f"{entry.get('Degree', '')} - {entry.get('Institution', '')}"
                elif section_name == "experience":
                    entry_summary += f"{entry.get('Job Title', '')} at {entry.get('Company', '')}"
                elif section_name == "projects":
                    entry_summary += f"{entry.get('Project Name', '')}"
                
                entry_label = ttk.Label(entries_frame, text=entry_summary)
                entry_label.pack(anchor=tk.W, pady=2)
                
                btn_frame = ttk.Frame(entries_frame)
                btn_frame.pack(fill=tk.X, pady=(0, 5))
                
                edit_btn = ttk.Button(btn_frame, text="Edit", 
                                     command=lambda idx=i: self.edit_entry(section_name, idx))
                edit_btn.pack(side=tk.LEFT, padx=2)
                
                delete_btn = ttk.Button(btn_frame, text="Delete", 
                                       command=lambda idx=i: self.delete_entry(section_name, idx))
                delete_btn.pack(side=tk.LEFT, padx=2)
                
                ttk.Separator(entries_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)
        
        # Add new entry button
        add_btn = ttk.Button(container, text=f"Add New {section_name[:-1].title()}", 
                            command=lambda: self.show_entry_form(section_name))
        add_btn.pack(anchor=tk.W, pady=10)
    
    def show_entry_form(self, section_name, entry_index=None):
        # Create a new window for the entry form
        entry_window = tk.Toplevel(self.root)
        entry_window.title(f"Add {section_name[:-1].title()}")
        entry_window.geometry("600x500")
        entry_window.minsize(600, 500)
        entry_window.configure(bg=self.bg_color)
        
        # Container
        main_frame = ttk.Frame(entry_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Form fields
        self.section_entries = {}
        
        for question in RESUME_SECTIONS[section_name]:
            frame = ttk.Frame(main_frame)
            frame.pack(fill=tk.X, pady=5)
            
            label = ttk.Label(frame, text=f"{question}:")
            label.pack(anchor=tk.W)
            
            if "description" in question.lower() or "responsibilities" in question.lower():
                # Use text area for longer text
                entry = scrolledtext.ScrolledText(frame, height=5, wrap=tk.WORD)
                # Fill with existing data if editing
                if entry_index is not None and self.resume_data[section_name][entry_index].get(question):
                    entry.insert(tk.END, self.resume_data[section_name][entry_index][question])
            else:
                # Use single line entry for shorter text
                entry = ttk.Entry(frame, width=50)
                # Fill with existing data if editing
                if entry_index is not None and self.resume_data[section_name][entry_index].get(question):
                    entry.insert(0, self.resume_data[section_name][entry_index][question])
            
            entry.pack(fill=tk.X)
            self.section_entries[question] = entry
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        save_btn = ttk.Button(button_frame, text="Save",
                             command=lambda: self.save_entry_form(section_name, entry_index, entry_window))
        save_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = ttk.Button(button_frame, text="Cancel",
                               command=entry_window.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        if entry_index is None:  # Only for new entries
            feedback_btn = ttk.Button(button_frame, text="Get AI Feedback",
                                     command=lambda: self.get_entry_feedback(section_name))
            feedback_btn.pack(side=tk.LEFT, padx=5)
    
    def save_entry_form(self, section_name, entry_index, window):
        # Collect data from form
        entry_data = {}
        for question, entry_widget in self.section_entries.items():
            if isinstance(entry_widget, scrolledtext.ScrolledText):
                value = entry_widget.get("1.0", tk.END).strip()
            else:
                value = entry_widget.get().strip()
            entry_data[question] = value
        
        # Initialize the section as a list if it's not already
        if not isinstance(self.resume_data.get(section_name, None), list):
            self.resume_data[section_name] = []
        
        # Update or add the entry
        if entry_index is not None:
            self.resume_data[section_name][entry_index] = entry_data
        else:
            self.resume_data[section_name].append(entry_data)
        
        # Close the form window
        window.destroy()
        
        # Refresh the section view
        self.show_section(section_name)
    
    def edit_entry(self, section_name, index):
        self.show_entry_form(section_name, index)
    
    def delete_entry(self, section_name, index):
        confirm = messagebox.askyesno("Confirm Delete", 
                                      "Are you sure you want to delete this entry?")
        if confirm:
            self.resume_data[section_name].pop(index)
            self.show_section(section_name)
    
    def save_section(self):
        # Collect data from current form
        section_data = {}
        for question, entry_widget in self.section_entries.items():
            if isinstance(entry_widget, scrolledtext.ScrolledText):
                value = entry_widget.get("1.0", tk.END).strip()
            else:
                value = entry_widget.get().strip()
            section_data[question] = value
        
        # Update resume data
        self.resume_data[self.current_section] = section_data
        
        messagebox.showinfo("Success", f"{self.current_section.replace('_', ' ').title()} section saved!")
    
    def get_section_feedback(self):
        # First save the current section
        self.save_section()
        
        # Get data for feedback
        section_text = "\n".join([f"{k}: {v}" for k, v in self.resume_data[self.current_section].items()])
        
        # Show "loading" feedback
        self.update_feedback("Getting AI feedback...")
        
        # Get feedback from AI
        feedback = self.get_ai_feedback(self.current_section, section_text)
        
        # Update the feedback area
        self.update_feedback(feedback)
    
    def get_entry_feedback(self, section_name):
        # Collect data from form
        entry_data = {}
        for question, entry_widget in self.section_entries.items():
            if isinstance(entry_widget, scrolledtext.ScrolledText):
                value = entry_widget.get("1.0", tk.END).strip()
            else:
                value = entry_widget.get().strip()
            entry_data[question] = value
        
        # Create text for feedback
        entry_text = "\n".join([f"{k}: {v}" for k, v in entry_data.items()])
        
        # Show "loading" feedback
        self.update_feedback("Getting AI feedback...")
        
        # Get feedback from AI
        feedback = self.get_ai_feedback(section_name[:-1], entry_text)
        
        # Update the feedback area
        self.update_feedback(feedback)
    
    def update_feedback(self, text):
        self.feedback_text.config(state=tk.NORMAL)
        self.feedback_text.delete("1.0", tk.END)
        self.feedback_text.insert(tk.END, text)
        self.feedback_text.config(state=tk.DISABLED)
        self.root.update_idletasks()
    
    def get_ai_feedback(self, section_name, content):
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
    
    def generate_ai_report(self):
        # First check if we have data for all sections
        for section in RESUME_SECTIONS:
            if not self.resume_data.get(section):
                messagebox.showwarning("Incomplete Resume", 
                                       f"Please complete the {section.replace('_', ' ').title()} section before generating a report.")
                return
        
        # Show loading message
        self.update_feedback("Analyzing your entire resume... This may take a moment.")
        
        # Get the AI report
        feedback = self.generate_ai_summary()
        
        # Update feedback area with the report
        self.update_feedback(feedback)
    
    def generate_ai_summary(self):
        """Generate an AI summary of the entire resume and provide overall feedback."""
        try:
            resume_text = json.dumps(self.resume_data, indent=2)
            
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
    
    def save_resume(self):
        # Check if we have personal info at minimum
        if not self.resume_data.get("personal_info"):
            messagebox.showwarning("Missing Information", 
                                   "Please complete at least the Personal Info section before saving.")
            return
        
        # Create resumes directory if it doesn't exist
        if not os.path.exists("resumes"):
            os.makedirs("resumes")
            
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name = "resume"
        if self.resume_data.get("personal_info") and self.resume_data["personal_info"].get("Full Name"):
            name = self.resume_data["personal_info"]["Full Name"].replace(" ", "_").lower()
        
        filename = f"resumes/{name}_{timestamp}.json"
        
        # Save the data
        with open(filename, "w") as f:
            json.dump(self.resume_data, f, indent=2)
            
        messagebox.showinfo("Resume Saved", f"Your resume has been saved to {filename}")

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = ResumeBuilderApp(root)
    root.mainloop() 