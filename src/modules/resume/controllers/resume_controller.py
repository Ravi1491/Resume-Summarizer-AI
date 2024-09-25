import os
import boto3
from flask import session, render_template, current_app, request, json,redirect,url_for, flash
from werkzeug.utils import secure_filename
from ..services.resume_service import ResumeService
from ..services.groq_service import GroqService
from ..utils.prompt import match_job_description_prompt,parsed_resume_prompt
from ..utils.helper import genrate_html
from src.services.aws import AwsService

s3 = boto3.client('s3')

class ResumeController():
  def __init__(self) -> None:
    self.resume_service = ResumeService()
    self.groq_service = GroqService()
  
  def home(self):
    user = session.get('user')
    all_user_resumes = self.resume_service.get_reusme_by_user_id(user_id=user['id'])
    all_user_resumes_dict = [resume.to_dict() for resume in all_user_resumes]
    return render_template('dashboard.html', uploaded_pdfs = all_user_resumes_dict)
  
  def compare_resume_with_job(self):
    if request.method == 'POST' and 'job_description' in request.form:
      if len(request.form['job_description']) == 0:
        flash('Job description cannot be empty.', 'error')
        return redirect(url_for('resume.home'))

      user = session.get('user')
      all_user_resumes = self.resume_service.get_reusme_by_user_id(user_id=user['id'])
      all_user_resumes_dict = [resume.to_dict() for resume in all_user_resumes]
      
      final_res = []
      for resume in all_user_resumes_dict:
        prompt = match_job_description_prompt(file_name=resume["filename"], ai_text=resume["ai_text"], job_description=request.form['job_description'])
        res = self.groq_service.get_response(prompt)
        sanitize_res = json.loads(res)
        final_res.append(sanitize_res)
        
      data = {
        'job_description': request.form['job_description'],
        'comparison_results': final_res
      }
      
      return render_template('compare.html', data=data)

    return render_template('compare.html')
  
  def get_resume_summary(self, id):
    try:
      resume = self.resume_service.get_resume_by_id(id=id)
      if resume:
        resume = resume.to_dict()
        resume_json = resume.get('ai_text')
        
        content = json.loads(resume_json)
          
        html = genrate_html(content)
        return render_template('view.html', pdf=html)
      else:
        return render_template('fallback.html')
    except Exception as e:
      print(f"An error occurred: {str(e)}")
      return render_template(('dashboard.html'))
  
  def delete_resume(self, id):
    try:
      self.resume_service.delete_resume_by_id(id=id)
      return redirect(url_for('resume.home'))
    except Exception as e:
      print(f"An error occurred: {str(e)}")
      return render_template(('dashboard.html'))
      
  def upload_resume(self):
    try:
      user = session.get('user')

      if 'pdfs' not in request.files:
        flash('No file part', 'error')
        return redirect(request.url)

      files = request.files.getlist('pdfs')
      for file in files:
        if file and self.resume_service.filter_file_by_extension(filename=file.filename):
          filename = secure_filename(file.filename)
          self.aws_service = AwsService()
          
          # Upload file to S3 and get the pre-signed URL
          key = self.aws_service.upload_file(file=file)
          presigned_url = self.aws_service.get_file(key)
          
          current_app.logger.info(f"File uploaded to S3: {filename}")

          try:
            # Use the pre-signed URL to extract text from the PDF
            text = self.resume_service.get_resume_pdf_text(file_url=presigned_url)
            current_app.logger.info(f"Text extracted from PDF: {text}")
            
            prompt = parsed_resume_prompt(text)
            combined_prompt = f"{prompt}\n\n{text}" if text else prompt
            generated_text = self.groq_service.get_response(prompt=combined_prompt)

            self.resume_service.create_resume(filename=key, ai_text=generated_text, text=text, user_id=user['id'])
            current_app.logger.info(f"Resume processed and saved: {filename}")
          except Exception as pdf_error:
            current_app.logger.error(f"Error processing PDF {filename}: {str(pdf_error)}")
            flash(f'Error processing {filename}. Please ensure it is a valid PDF.', 'error')
        else:
          current_app.logger.warning(f'File {file.filename} is not a valid PDF')
          flash(f'File {file.filename} is not a valid PDF', 'warning')

      return redirect(url_for('resume.home'))
    except Exception as e:
      current_app.logger.error(f"An error occurred during resume upload: {str(e)}")
      flash('An error occurred during file upload. Please try again.', 'error')
      return redirect(url_for('resume.home'))
