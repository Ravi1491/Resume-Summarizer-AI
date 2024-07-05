from flask import render_template, request, redirect, flash, url_for, Blueprint, current_app
from werkzeug.utils import secure_filename
from .models import get_all_pdfs, delete_pdf_entry, get_pdf_by_id
from .utils import get_resume_pdf_text, generate_text, allowed_file
import os
import sqlite3
import json
from .utils import dict_to_html_table

app = Blueprint('app', __name__)

@app.route('/')
def index():
    uploaded_pdfs = get_all_pdfs()
    # return "Hello"
    return render_template('upload.html', uploaded_pdfs=uploaded_pdfs)

@app.route('/compare')
def compare():
    return render_template('compare.html')

@app.route('/view/<int:id>')
def view_pdf(id):
    pdf = get_pdf_by_id(id)
    if pdf:
        content = json.loads(pdf[2])
        html_table = dict_to_html_table(content)
        return render_template('view.html', pdf=html_table)
    else:
        flash('PDF not found')
        return redirect(url_for('app.index'))

@app.route('/delete/<int:id>', methods=['POST'])
def delete_pdf(id):
    delete_pdf_entry(id)
    return redirect(url_for('app.index'))

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'pdfs' not in request.files:
        flash('No file part')
        return redirect(request.url)

    files = request.files.getlist('pdfs')
    saved_files = []

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            saved_files.append(filename)
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO pdfs (filename) VALUES (?)', (filename,))
                conn.commit()
        else:
            flash(f'File {file.filename} is not a valid PDF')

    if saved_files:
        flash(f'Successfully uploaded: {", ".join(saved_files)}')
        all_pdfs = get_all_pdfs()

        for pdf in all_pdfs:
            filename = pdf[1]
            text = get_resume_pdf_text(f'uploads/{filename}')
            prompt = f"""You are Experience Software Developer. You will have to make summary of resumes section wise.
            Your role is to summarize the resume in a way that it is easy to read and understand.
            Divide the summary in following sections:
            1. Personal_Information
            2. Objective
            3. Work Experience
            4. Education
            5. Skills
            6. Projects
            7. Certifications
            8. Hobbies
            9. Languages
            10. References

            If some section is missing, you can skip that section.
            Only give the response in JSON format.
            Don't give any text outside the JSON. Only provide JSON. 
            Even Don't include Here is the summary of the resume in JSON format: 
            Here is the text from the resume: {text}"""

            generated_text = generate_text(prompt, text)

            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE pdfs SET text = ?, ai_text = ? WHERE id = ?', (text, generated_text, pdf[0]))
                conn.commit()
            flash(generated_text)
    else:
        flash('No valid files uploaded')

    return redirect(url_for('app.index'))
