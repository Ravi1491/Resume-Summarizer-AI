from flask import Flask, render_template, url_for,request, redirect,flash
from werkzeug.utils import secure_filename
from pdfminer3.layout import LAParams
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter

import os
import io
from groq import Groq
from flask_session import Session
import sqlite3
from config import DevelopmentConfig, ProductionConfig

app = Flask(__name__)

if os.getenv('CONFIG_MODE') == 'development':
  app.config.from_object(DevelopmentConfig)
else:
  app.config.from_object(ProductionConfig)

app.secret_key = app.config['SECRET_KEY']

Session(app)

if not os.path.exists(app.config['UPLOAD_FOLDER']):
  os.makedirs(app.config['UPLOAD_FOLDER'])

client = Groq(
  api_key=app.config['GROQ_API_KEY'],
)

def init_db():
  with sqlite3.connect('database.db') as conn:
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS pdfs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        filename TEXT NOT NULL,
                        text TEXT NULL,
                        ai_text TEXT NULL,
                        upload_id INTEGER
                    )''')
    conn.commit()

@app.route('/')
def index():
  uploaded_pdfs = get_all_pdfs()
  
  return render_template('upload.html', uploaded_pdfs=uploaded_pdfs)

@app.route('/compare',)
def compare():
  return render_template('compare.html')

@app.route('/view/<int:id>')
def view_pdf(id):
  with sqlite3.connect('database.db') as conn:
    cursor = conn.cursor()
    cursor.execute('SELECT filename, text, ai_text FROM pdfs WHERE id = ?', (id,))
    pdf = cursor.fetchone()
    if pdf:
      return render_template('view.html', pdf=pdf)
    else:
      flash('PDF not found')
      return redirect(url_for('index'))

def allowed_file(filename):
  return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/delete/<int:id>', methods=['POST'])
def delete_pdf(id):

  with sqlite3.connect('database.db') as conn:
    cursor = conn.cursor()
    cursor.execute('SELECT filename FROM pdfs WHERE id = ?', (id,))
    pdf = cursor.fetchone()
    if pdf:
      filename = pdf[0]
      cursor.execute('DELETE FROM pdfs WHERE id = ?', (id,))
      conn.commit()
      os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
      flash(f'Successfully deleted: {filename}')
    else:
      flash('PDF not found')
  return redirect(url_for('index'))

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
      file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
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
      prompt = f"Here is the text from the resume {text}"
      generated_text = generate_text(prompt, text)
      
      with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE pdfs SET text = ?, ai_text = ? WHERE id = ?', (text, generated_text, pdf[0]))
        conn.commit()
      # print(generated_text)
      flash(generated_text)
      
  else:
    flash('No valid files uploaded')

  return redirect(url_for('index'))

def get_all_pdfs():
  with sqlite3.connect('database.db') as conn:
    cursor = conn.cursor()
    cursor.execute('SELECT id, filename, text, ai_text FROM pdfs')
    return cursor.fetchall()

def get_resume_pdf_text(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
          caching=True,
          check_extractable=True):
          page_interpreter.process_page(page)
    
        text = fake_file_handle.getvalue()

    # close open handles
    converter.close()
    fake_file_handle.close()
    return text

def generate_text(prompt, text):
    combined_prompt=''

    if len(text) > 0:
       combined_prompt = f"{prompt}\n\n{text}"
    else:
        combined_prompt = prompt

    chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": combined_prompt,
            
        }
    ],
    model="llama3-70b-8192",
)
    text = chat_completion.choices[0].message.content
    print(chat_completion)
    return text


if __name__ == '__main__':
  init_db()
  
  app.run(debug=True)