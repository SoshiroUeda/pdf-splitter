from flask import Flask, request, render_template, send_file
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO
import logging
import base64
import zipfile  # ← 追加

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)

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
            page_count = len(reader.pages)

            if action == 'split_range':
                encoded = base64.b64encode(file_bytes).decode('utf-8')
                return render_template('index.html', page_count=page_count, action='split_range', file_data=encoded)

            elif action == 'split_all':
                try:
                    chunk_size = max(1, int(request.form.get('chunk_size', '1')))
                    output_zip = BytesIO()
                    with zipfile.ZipFile(output_zip, 'w') as zipf:
                        for i in range(0, len(reader.pages), chunk_size):
                            writer = PdfWriter()
                            for j in range(i, min(i + chunk_size, len(reader.pages))):
                                writer.add_page(reader.pages[j])
                            pdf_bytes = BytesIO()
                            writer.write(pdf_bytes)
                            zipf.writestr(f'part_{i // chunk_size + 1}.pdf', pdf_bytes.getvalue())
                    output_zip.seek(0)
                    return send_file(output_zip, as_attachment=True, download_name='split_pages.zip', mimetype='application/zip')
                except Exception as e:
                    logging.error(f"Error in split_all: {e}")
                    return f"Error: {e}", 500

        elif action == 'extract_selected':
            try:
                selected_pages = request.form.getlist('selected_pages')
                encoded_data = request.form.get('file_data')
                file_bytes = base64.b64decode(encoded_data)
                reader = PdfReader(BytesIO(file_bytes))
                writer = PdfWriter()

                for page_index in selected_pages:
                    i = int(page_index)
                    if 0 <= i < len(reader.pages):
                        writer.add_page(reader.pages[i])

                output = BytesIO()
                writer.write(output)
                output.seek(0)
                return send_file(output, as_attachment=True, download_name='selected_pages.pdf', mimetype='application/pdf')
            except Exception as e:
                logging.error(f"Error in extract_selected: {e}")
                return f"Error: {e}", 500

    return render_template('index.html')
