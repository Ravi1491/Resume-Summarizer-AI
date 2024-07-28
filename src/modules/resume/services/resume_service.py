import sqlite3
import os
import io
from pdfminer3.layout import LAParams
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer3.converter import TextConverter
from flask import current_app

class ResumeService():
  def create_resume(self,filename, text, ai_text, user_id):
    with sqlite3.connect('database.db') as conn:
      cursor = conn.cursor()
      cursor.execute('INSERT INTO pdfs (filename, text, ai_text, user_id) VALUES (?,?,?,?)', (filename,text, ai_text,user_id,))
      conn.commit()

  def get_reusme_by_user_id(self,user_id):
    with sqlite3.connect('database.db') as conn:
      cursor = conn.cursor()
      cursor.execute('SELECT id, filename, text, ai_text FROM pdfs WHERE user_id = ?', (user_id,))
      return cursor.fetchall()
    
  def get_resume_by_id(self,id):
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT filename, text, ai_text FROM pdfs WHERE id = ?', (id,))
        return cursor.fetchone()
  
  def delete_resume_by_id(self,id):
    with sqlite3.connect('database.db') as conn:
      cursor = conn.cursor()
      cursor.execute('SELECT filename FROM pdfs WHERE id = ?', (id,))
      resume = cursor.fetchone()
      if resume:
          filename = resume[0]
          cursor.execute('DELETE FROM pdfs WHERE id = ?', (id,))
          conn.commit()
          os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
      
  def filter_file_by_extension(self,filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

  def get_resume_pdf_text(self,file):
      resource_manager = PDFResourceManager()
      fake_file_handle = io.StringIO()
      converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
      page_interpreter = PDFPageInterpreter(resource_manager, converter)
      with open(file, 'rb') as fh:
          for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
              page_interpreter.process_page(page)
          text = fake_file_handle.getvalue()

      converter.close()
      fake_file_handle.close()
      return text
