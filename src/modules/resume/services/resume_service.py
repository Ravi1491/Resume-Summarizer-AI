from database.models.resume import Resume
from database import db

import os
import io
import requests
from pdfminer3.layout import LAParams
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer3.converter import TextConverter
from flask import current_app

class ResumeService():
  @staticmethod
  def create_resume(filename, text, ai_text, user_id):
    resume = Resume(filename, text, ai_text, user_id)
    db.session.add(resume)
    db.session.commit()

  def get_reusme_by_user_id(self,user_id):
    return Resume.query.filter(Resume.user_id == user_id).all()
    
  def get_resume_by_id(self,id):
    return Resume.query.filter(Resume.id == id).first()
  
  def delete_resume_by_id(self,id):
    resume = Resume.query.filter(Resume.id == id).first()
    if resume:
      db.session.delete(resume)
      db.session.commit()
      os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], resume.filename))

  def filter_file_by_extension(self,filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

  def get_resume_pdf_text(self, file_url):
    # Download the PDF content from the pre-signed URL
    response = requests.get(file_url)
    response.raise_for_status()  # Raise an exception for bad responses
    
    # Create a file-like object from the downloaded content
    pdf_file = io.BytesIO(response.content)

    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)

    for page in PDFPage.get_pages(pdf_file, caching=True, check_extractable=True):
        page_interpreter.process_page(page)

    text = fake_file_handle.getvalue()

    # Close open handles
    converter.close()
    fake_file_handle.close()
    pdf_file.close()

    return text
