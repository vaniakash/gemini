# AI Resume Builder

A complete resume building solution with both GUI and command-line interfaces, powered by AI feedback.

## Features

- Graphical user interface built with Tkinter
- Interactive resume builder with sections navigation
- Real-time AI feedback on your resume content
- Personalized suggestions for improvement
- Ability to add multiple entries for education, experience, and projects
- Complete resume analysis with strengths and recommendations
- Saves resume data in JSON format

## Requirements

- Python 3.7+
- Tkinter (comes with standard Python installation)
- Internet connection (for API access)

## Installation

1. Clone or download this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### GUI Application

Run the GUI application with:

```bash
python ai_resume_builder_gui.py
```

The GUI provides an intuitive interface to:
- Navigate between resume sections
- Save individual sections as you complete them
- Get AI feedback on your entries
- Edit and delete entries
- Generate a comprehensive AI report on your entire resume
- Save your resume as a JSON file

### Command-Line Application

Run the command-line version with:

```bash
python ai_resume_builder.py
```

Follow the interactive prompts to complete each section of your resume. The AI will provide suggestions for improvement as you go.

## Resume Sections

Both applications help you build these standard resume sections:

- Personal Information
- Professional Summary
- Education
- Work Experience
- Skills
- Projects
- Certifications

## Notes

- The AI feedback is powered by Google's Gemini API
- You may occasionally hit API rate limits if you make too many requests in a short time
- For best results, be detailed and specific in your resume entries 