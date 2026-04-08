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



@app.route('/generate', methods=['POST'])
def generate():
    try:
        if sys.platform == "win32":
            import pythoncom
            pythoncom.CoInitialize()

        form = request.form

        base_data = {
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
                title = f'Experiment {num}'
            titles.append(title)

        # Helper to render a single page based on title length
        def render_practical_page(practical_idx, title):
            page_data = base_data.copy()
            page_data['practical_no'] = practical_numbers[practical_idx]
            
            if len(title) > 100:
                # Very long title → template2.docx
                tpl_path = 'template2.docx'
                page_data['titleeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'] = title
            elif len(title) > 43:
                # Medium title → template.docx
                tpl_path = 'template.docx'
                page_data['titleeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'] = title
            else:
                # Short title → template1.docx
                tpl_path = 'template1.docx'
                page_data['title'] = title
                
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