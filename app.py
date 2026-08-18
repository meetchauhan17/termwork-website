import os
import re
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

    CSE title ranges:
      - <= 43 chars        → template1.docx
      - 44 – 115 chars     → template.docx
      - > 115 chars        → template2.docx

    IT title ranges:
      - <= 43 chars        → tempitfor43wordtitle.docx
      - 44 – 115 chars     → tempitfo44to115rwordtitle.docx
      - 116 – 180 chars    → tempitfor115to180wordtitle.docx
    """
    branch_key = (branch or 'cse').strip().lower()

    if title_length > 115:
        category = 'long'
    elif title_length > 43:
        category = 'medium'
    else:
        category = 'short'

    # Direct file mapping — no fallback lists needed
    templates = {
        'cse': {
            'short':  'template1.docx',
            'medium': 'template.docx',
            'long':   'template2.docx',
        },
        'it': {
            'short':  'tempitfor43wordtitle.docx',
            'medium': 'tempitfo44to115rwordtitle.docx',
            'long':   'tempitfor115to180wordtitle.docx',
        },
    }

    if branch_key not in templates:
        raise ValueError(f"Unsupported branch '{branch}'. Only 'CSE' and 'IT' are supported.")

    selected_path = templates[branch_key][category]

    if not os.path.exists(selected_path):
        raise FileNotFoundError(
            f"Template '{selected_path}' for branch '{branch}' ({category} title) not found."
        )

    return selected_path


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
            page_data['titleeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'] = title
            
            tpl_path = get_template_path(branch, len(title))
                
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
            
            # Append subsequent pages — each on a guaranteed new page
            for idx in range(1, count):
                page_tpl = render_practical_page(idx, titles[idx])

                # Find section properties in final_doc to insert before it
                final_sect_pr = None
                for child in final_doc.element.body:
                    if child.tag.endswith('sectPr'):
                        final_sect_pr = child
                        break

                # --- Hard page break paragraph ---
                # Guarantees this practical always starts on a fresh page,
                # no matter what the template's own sectPr says.
                WORD_NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
                pb_para  = etree.Element(f'{{{WORD_NS}}}p')
                pb_run   = etree.SubElement(pb_para, f'{{{WORD_NS}}}r')
                pb_break = etree.SubElement(pb_run,  f'{{{WORD_NS}}}br')
                pb_break.set(f'{{{WORD_NS}}}type', 'page')

                if final_sect_pr is not None:
                    final_sect_pr.addprevious(pb_para)
                else:
                    final_doc.element.body.append(pb_para)

                # Append all body elements from rendered template
                for element in page_tpl.element.body:
                    if element.tag.endswith('sectPr'):
                        continue
                    if final_sect_pr is not None:
                        final_sect_pr.addprevious(copy.deepcopy(element))
                    else:
                        final_doc.element.body.append(copy.deepcopy(element))
                        
        except FileNotFoundError as fnf_err:
            return jsonify({'success': False, 'message': str(fnf_err)})

        # --- Build pretty filename: last-3-digits-of-PEN + subject ---
        pen     = form.get('pen', '').strip()
        subject = form.get('subject', '').strip()
        pen_suffix  = pen[-3:] if len(pen) >= 3 else pen.zfill(3)
        # Sanitize subject: keep letters, digits, spaces, hyphens
        safe_subject = re.sub(r'[^\w\s\-]', '', subject).strip()
        safe_subject = re.sub(r'\s+', ' ', safe_subject)  # collapse whitespace
        base_name = f"{pen_suffix}_{safe_subject}" if safe_subject else f"{pen_suffix}_Termwork"

        output_docx = f'outputs/{base_name}.docx'
        output_pdf  = f'outputs/{base_name}.pdf'

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
            'download_pdf':  f'/download/pdf/{base_name}',
            'download_docx': f'/download/docx/{base_name}'
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error occurred: {str(e)}'})


@app.route('/download/<file_type>/<path:base_name>')
def download(file_type, base_name):
    if file_type == 'pdf':
        path        = f'outputs/{base_name}.pdf'
        dl_name     = f'{base_name}.pdf'
    else:
        path        = f'outputs/{base_name}.docx'
        dl_name     = f'{base_name}.docx'

    if os.path.exists(path):
        return send_file(path, as_attachment=True, download_name=dl_name)
    return "File not found", 404


if __name__ == '__main__':
    app.run(debug=True, port=5000)