import os
import copy
import sys
import subprocess
from flask import Flask, render_template, request, send_file, jsonify
from docx import Document
from lxml import etree

if sys.platform == "win32":
    import pythoncom
    from docx2pdf import convert

app = Flask(__name__)

# Ensure directories exist
os.makedirs('temp', exist_ok=True)
os.makedirs('outputs', exist_ok=True)


def replace_text_in_paragraph(paragraph, data):
    """Replace {{placeholder}} tags in a paragraph with actual values."""
    for key, val in data.items():
        placeholder = f"{{{{{key}}}}}"
        if placeholder in paragraph.text:
            text = paragraph.text.replace(placeholder, str(val))
            paragraph.text = text


def replace_text_in_doc(doc, data):
    """Replace placeholders in all paragraphs and table cells of a document."""
    for p in doc.paragraphs:
        replace_text_in_paragraph(p, data)

    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    replace_text_in_paragraph(p, data)
                for nested_table in cell.tables:
                    for n_row in nested_table.rows:
                        for n_cell in n_row.cells:
                            for np in n_cell.paragraphs:
                                replace_text_in_paragraph(np, data)


@app.route('/')
def home():
    return render_template('index.html')


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

        count = int(form.get('practical_count', 0))
        if count == 0:
            return jsonify({'success': False, 'message': 'Number of practicals must be greater than 0.'})

        titles = []
        for i in range(1, count + 1):
            title = form.get(f'title_{i}', '').strip()
            if not title:
                title = f'Experiment {i}'
            titles.append(title)

        template_path = 'template.docx'
        if not os.path.exists(template_path):
            return jsonify({'success': False, 'message': 'Template file not found. Please ensure template.docx is in the project root.'})

        # Build the first practical from the template
        final_doc = Document(template_path)
        first_data = base_data.copy()
        first_data['practical_no'] = 1
        first_data['titleffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'] = titles[0]
        replace_text_in_doc(final_doc, first_data)

        # For each additional practical, deep-copy the template, replace, and append
        for i in range(1, count):
            # Add a page break before the next practical
            final_doc.add_page_break()

            tmp_doc = Document(template_path)
            page_data = base_data.copy()
            page_data['practical_no'] = i + 1
            page_data['titleffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'] = titles[i]
            replace_text_in_doc(tmp_doc, page_data)

            # Find section properties in final_doc to insert before it
            final_sect_pr = None
            for child in final_doc.element.body:
                if child.tag.endswith('sectPr'):
                    final_sect_pr = child
                    break

            # Append all body elements from tmp_doc into final_doc before sectPr
            for element in tmp_doc.element.body:
                if element.tag.endswith('sectPr'):
                    continue
                if final_sect_pr is not None:
                    final_sect_pr.addprevious(copy.deepcopy(element))
                else:
                    final_doc.element.body.append(copy.deepcopy(element))

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