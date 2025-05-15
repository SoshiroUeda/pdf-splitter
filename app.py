from flask import Flask, request, render_template, send_file
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO
import logging
import base64
import zipfile
import os

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # 最大20MB

def split_all_pages(reader, chunk_size, base_name):
    output_zip = BytesIO()
    with zipfile.ZipFile(output_zip, 'w') as zipf:
        for i in range(0, len(reader.pages), chunk_size):
            writer = PdfWriter()
            for j in range(i, min(i + chunk_size, len(reader.pages))):
                writer.add_page(reader.pages[j])
            pdf_bytes = BytesIO()
            writer.write(pdf_bytes)
            zipf.writestr(f'{base_name}_part_{i // chunk_size + 1}.pdf', pdf_bytes.getvalue())
    output_zip.seek(0)
    return output_zip

def extract_selected_pages(reader, selected_pages):
    writer = PdfWriter()
    for i in selected_pages:
        if 0 <= i < len(reader.pages):
            writer.add_page(reader.pages[i])
    output = BytesIO()
    writer.write(output)
    output.seek(0)
    return output

def extract_page_range(reader, start, end):
    writer = PdfWriter()
    for i in range(start, end + 1):
        if 0 <= i < len(reader.pages):
            writer.add_page(reader.pages[i])
    output = BytesIO()
    writer.write(output)
    output.seek(0)
    return output

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        action = request.form.get('action')

        if 'file' in request.files:
            file = request.files['file']
            if not file or file.filename == '':
                return "Error: No file uploaded", 400
            if not file.filename.lower().endswith('.pdf'):
                return "Error: Only PDF files are supported", 400

            file_bytes = file.read()
            reader = PdfReader(BytesIO(file_bytes))
            base_name = os.path.splitext(file.filename)[0]

            if action == 'split_all':
                try:
                    chunk_size = max(1, int(request.form.get('chunk_size', '1')))
                    output_zip = split_all_pages(reader, chunk_size, base_name)
                    return send_file(output_zip, as_attachment=True, download_name='split_pages.zip', mimetype='application/zip')
                except Exception as e:
                    logging.error(f"Error in split_all: {e}")
                    return f"Error: {e}", 500

            elif action == 'split_range':
                try:
                    start = int(request.form.get('start_page')) - 1
                    end = int(request.form.get('end_page')) - 1
                    output = extract_page_range(reader, start, end)
                    return send_file(output, as_attachment=True, download_name='range_pages.pdf', mimetype='application/pdf')
                except Exception as e:
                    logging.error(f"Error in split_range: {e}")
                    return f"Error: {e}", 500

        elif action == 'extract_selected':
            try:
                selected_pages = [int(i) for i in request.form.getlist('selected_pages')]
                encoded_data = request.form.get('file_data')
                file_bytes = base64.b64decode(encoded_data)
                reader = PdfReader(BytesIO(file_bytes))
                output = extract_selected_pages(reader, selected_pages)
                return send_file(output, as_attachment=True, download_name='selected_pages.pdf', mimetype='application/pdf')
            except Exception as e:
                logging.error(f"Error in extract_selected: {e}")
                return f"Error: {e}", 500

    return render_template('index.html')
