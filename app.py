import os
import copy
import sys
import subprocess
from flask import Flask, render_template, request, send_file, jsonify
from docxtpl import DocxTemplate
from docx import Document
from lxml import etree

if sys.platform == "win32":
    import pythoncom
    from docx2pdf import convert

app = Flask(__name__)

# Ensure directories exist
os.makedirs('temp', exist_ok=True)
os.makedirs('outputs', exist_ok=True)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/keep-alive')
def keep_alive():
    """Lightweight endpoint for UptimeRobot to ping and prevent Render from sleeping."""
    return "I am awake!", 200



def get_template_path(branch, title_length):
    """
    Select the appropriate Word template based on branch and title length.
    - title_length <= 43: short title (template1)
    - 44 <= title_length <= 115: medium title (template)
    - title_length > 115: long title (template2)
    
    Supports branch-specific naming patterns (e.g. tempitfor65wordtitle.docx, template_it.docx, template1_it.docx)
    with fallback to default CSE templates (template1.docx, template.docx, template2.docx).
    """
    branch_key = (branch or 'cse').strip().lower()

    if title_length > 115:
        category = 'long'
    elif title_length > 43:
        category = 'medium'
    else:
        category = 'short'

    it_candidates = {
        'short': [
            'template1_it.docx',
            'it_template1.docx',
            'tempitfor65wordtitle.docx',
            'templates_docx/it/template1.docx',
            'templates/it/template1.docx',
            'template1.docx'
        ],
        'medium': [
            'tempitfor65wordtitle.docx',
            'template_it.docx',
            'it_template.docx',
            'templates_docx/it/template.docx',
            'templates/it/template.docx',
            'template.docx'
        ],
        'long': [
            'template2_it.docx',
            'it_template2.docx',
            'tempitfor65wordtitle.docx',
            'templates_docx/it/template2.docx',
            'templates/it/template2.docx',
            'template2.docx'
        ]
    }

    general_candidates = {
        'short': [
            f'template1_{branch_key}.docx',
            f'{branch_key}_template1.docx',
            f'templates_docx/{branch_key}/template1.docx',
            f'templates/{branch_key}/template1.docx',
            'template1.docx'
        ],
        'medium': [
            f'template_{branch_key}.docx',
            f'{branch_key}_template.docx',
            f'templates_docx/{branch_key}/template.docx',
            f'templates/{branch_key}/template.docx',
            'template.docx'
        ],
        'long': [
            f'template2_{branch_key}.docx',
            f'{branch_key}_template2.docx',
            f'templates_docx/{branch_key}/template2.docx',
            f'templates/{branch_key}/template2.docx',
            'template2.docx'
        ]
    }

    candidates = it_candidates[category] if branch_key == 'it' else general_candidates[category]
    title_key = 'title' if category == 'short' else 'titleeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'

    selected_path = None
    for candidate in candidates:
        if os.path.exists(candidate):
            selected_path = candidate
            break

    if not selected_path:
        default_file = 'template1.docx' if category == 'short' else ('template2.docx' if category == 'long' else 'template.docx')
        if os.path.exists(default_file):
            selected_path = default_file
        else:
            raise FileNotFoundError(f"Template for branch '{branch}' ({category} title) not found.")

    return selected_path, title_key


@app.route('/generate', methods=['POST'])
def generate():
    try:
        if sys.platform == "win32":
            import pythoncom
            pythoncom.CoInitialize()

        form = request.form

        branch = form.get('branch', '').strip().upper()
        if not branch:
            class_val = form.get('class', '').strip().upper()
            if class_val:
                branch = class_val.split('-')[0].strip()

        base_data = {
            "branch": branch,
            "term": form.get('term', ''),
            "subject": form.get('subject', ''),
            "pen": form.get('pen', ''),
            "semester": form.get('semester', ''),
            "name": form.get('name', ''),
            "class": form.get('class', ''),
            "batch": form.get('batch', ''),
            "checked_by": form.get('checked_by', '')
        }

        practical_start = int(form.get('practical_start', 0))
        practical_end = int(form.get('practical_end', 0))
        if practical_start == 0 or practical_end == 0 or practical_end < practical_start:
            return jsonify({'success': False, 'message': 'Please enter valid Start and End practical numbers.'})

        count = practical_end - practical_start + 1
        practical_numbers = list(range(practical_start, practical_end + 1))

        titles = []
        for num in practical_numbers:
            title = form.get(f'title_{num}', '').strip()
            if not title:
                title = f'ㅤ'
            # Auto-shorten titles with 200+ characters at the last full stop before 200
            if len(title) >= 200:
                cut = title.rfind('.', 0, 200)
                if cut != -1:
                    title = title[:cut + 1].strip()
            titles.append(title)

        # Helper to render a single page based on branch and title length
        def render_practical_page(practical_idx, title):
            page_data = base_data.copy()
            page_data['practical_no'] = practical_numbers[practical_idx]
            page_data['title'] = title
            page_data['titleeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'] = title
            
            tpl_path, _ = get_template_path(branch, len(title))
                
            if not os.path.exists(tpl_path):
                raise FileNotFoundError(f"Template '{tpl_path}' is missing.")
                
            tpl = DocxTemplate(tpl_path)
            tpl.render(page_data)
            return tpl
            
        try:
            # Render first page to initialize the final document
            first_tpl = render_practical_page(0, titles[0])
            temp_first = 'temp/first_page.docx'
            first_tpl.save(temp_first)
            final_doc = Document(temp_first)
            
            # Append subsequent pages
            for idx in range(1, count):
                page_tpl = render_practical_page(idx, titles[idx])
                
                # Find section properties in final_doc to insert before it
                final_sect_pr = None
                for child in final_doc.element.body:
                    if child.tag.endswith('sectPr'):
                        final_sect_pr = child
                        break

                # Append all body elements from rendered template into final_doc before sectPr
                for element in page_tpl.element.body:
                    if element.tag.endswith('sectPr'):
                        continue
                    if final_sect_pr is not None:
                        final_sect_pr.addprevious(copy.deepcopy(element))
                    else:
                        final_doc.element.body.append(copy.deepcopy(element))
                        
        except FileNotFoundError as fnf_err:
            return jsonify({'success': False, 'message': str(fnf_err)})

        output_docx = 'outputs/Termwork.docx'
        output_pdf = 'outputs/Termwork.pdf'

        final_doc.save(output_docx)

        # Convert to PDF dynamically based on OS
        if sys.platform == "win32":
            # For local Windows execution
            convert(output_docx, output_pdf)
        else:
            # For Linux / Docker execution (using LibreOffice)
            subprocess.run(['libreoffice', '--headless', '--convert-to', 'pdf', output_docx, '--outdir', 'outputs'])

        # Clean up temp files
        if os.path.exists(temp_first):
            os.remove(temp_first)

        return jsonify({
            'success': True,
            'message': 'Termwork generated successfully!',
            'download_pdf': '/download/pdf',
            'download_docx': '/download/docx'
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error occurred: {str(e)}'})


@app.route('/download/<file_type>')
def download(file_type):
    if file_type == 'pdf':
        path = 'outputs/Termwork.pdf'
    else:
        path = 'outputs/Termwork.docx'

    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return "File not found", 404


if __name__ == '__main__':
    app.run(debug=True, port=5000)