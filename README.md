# Termwork Generator Pro

A complete Flask-based web application to generate multi-page Word and PDF documents from a template dynamically.

## Features
- Dynamic form inputs based on number of practicals requested
- Word document template replacement (`python-docx`)
- Proper page duplication & merging (`docxcompose`) 
- PDF Conversion (`docx2pdf`)
- Save & Load form data automatically via `localStorage`
- Modern, clean, and responsive UI built using Bootstrap 5

## Setup Instructions

1. **Install Requirements**
   Open your terminal inside the `termwork-website` folder and run the command:
   ```bash
   pip install -r requirements.txt
   ```

2. **Required Template Location**
   Ensure an actual Word file named `template.docx` exists in the `termwork-website` folder.
   
3. **Run the Application**
   ```bash
   python app.py
   ```

4. **Access UI**
   Open your browser and navigate to: `http://127.0.0.1:5000`

## Required Template Placeholders
In your `template.docx`, include the following tags. They will be replaced dynamically:
- `{{term}}`
- `{{subject}}`
- `{{name}}`
- `{{pen}}`
- `{{class}}`
- `{{batch}}`
- `{{semester}}`
- `{{checked_by}}`
- `{{title}}`
- `{{practical_no}}`

## Example Inputs
- **Name of Student:** Meet Chauhan
- **PEN:** 190XXXXX
- **Class:** B.Tech CS
- **Batch:** B2
- **Semester:** 6th
- **Subject:** Cloud Computing
- **Term:** Even 2024
- **Checked By:** Prof. Smith
- **Number of Practicals:** 5
- **Experiment 1 Title:** Installing AWS CLI
- **Experiment 2 Title:** Creating EC2 Instance
- ... and so on.

## Error Fixes Guide
1. **Docx2pdf Freezing / COM Error**
   - Ensure you are running this on a Windows Machine with Microsoft Office/Word installed, as `docx2pdf` replies on it.
   - If Flask hangs or throws threading COM errors during conversion, the `pythoncom.CoInitialize()` has been properly integrated into the codebase inside the request route. Make sure `pywin32` is correctly installed via the auto-generated `requirements.txt`.
2. **"Template file not found" Error**
   - The app explicitly looks for `template.docx` inside the root folder alongside `app.py`. Check for typos or file extension issues.
3. **Missing specific styles after generation**
   - The plugin `docxcompose` manages complex format merging significantly better than manual `lxml` body hacking, preventing files from being corrupt upon download. Ensure not to excessively overlap merged images in tables.

Enjoy using Termwork Generator Pro!
