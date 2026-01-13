from database.models.resume import Resume
from database import db

import os
import io
import requests
import re
from pdfminer3.layout import LAParams
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer3.converter import TextConverter
from flask import current_app

class ResumeService():
  @staticmethod
  def create_resume(filename, file_key, text, ai_text, user_id):
    resume = Resume(filename, file_key, text, ai_text, user_id)
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

  def filter_file_by_extension(self,filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

  def _clean_extracted_text(self, text):
    """
    Clean the extracted PDF text to fix common issues like:
    - Characters on separate lines
    - Excessive whitespace
    - Broken words
    """
    if not text:
      return ""
    
    # Replace multiple newlines with single newlines
    text = re.sub(r'\n+', '\n', text)
    
    # Replace multiple spaces with single space
    text = re.sub(r' +', ' ', text)
    
    # Fix broken words that are split across lines
    # Look for patterns like "word-\nword" or "word \nword"
    text = re.sub(r'(\w+)[-\s]*\n(\w+)', r'\1\2', text)
    
    # Remove leading/trailing whitespace from each line
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
      line = line.strip()
      if line:  # Only add non-empty lines
        cleaned_lines.append(line)
    
    # Join lines back together
    cleaned_text = '\n'.join(cleaned_lines)
    
    # Final cleanup: remove excessive whitespace
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
    
    return cleaned_text.strip()

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

    # Clean the extracted text
    cleaned_text = self._clean_extracted_text(text)
    
    return cleaned_text
