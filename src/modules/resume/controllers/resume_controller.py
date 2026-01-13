import os
import boto3
import re
from flask import session, render_template, current_app, request, json,redirect,url_for, flash
from werkzeug.utils import secure_filename
from ..services.resume_service import ResumeService
from src.utils.prompt import match_job_description_prompt,parsed_resume_prompt
from src.utils.helper import genrate_html
from src.services.aws import AwsService
from src.services.llm import LLMService
s3 = boto3.client('s3')

class ResumeController():
  def __init__(self) -> None:
    self.resume_service = ResumeService()
    self.llm_service = LLMService()
  
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
        res = self.llm_service.get_groq_response(prompt)
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
        
        print("resume_json ====== ", resume_json)
        
        content = json.loads(resume_json)
        
        print("content ====== ", content)
          
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
  
  def _extract_json_from_response(self, response_text):
    """
    Extract JSON from LLM response that may contain explanatory text.
    """
    if not response_text:
      return None
    
    # Try to find JSON content between triple backticks
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
    if json_match:
      return json_match.group(1)
    
    # Try to find JSON content between single backticks
    json_match = re.search(r'`(\{.*?\})`', response_text, re.DOTALL)
    if json_match:
      return json_match.group(1)
    
    # Try to find JSON object starting with { and ending with }
    json_match = re.search(r'(\{.*\})', response_text, re.DOTALL)
    if json_match:
      return json_match.group(1)
    
    # If no JSON found, return the original text
    return response_text
  
  def _truncate_text_for_llm(self, text, max_chars=8000):
    """
    Truncate text to fit within LLM context limits.
    Preserves complete sentences where possible.
    """
    if len(text) <= max_chars:
      return text
    
    # Try to truncate at a sentence boundary
    truncated = text[:max_chars]
    last_period = truncated.rfind('.')
    last_exclamation = truncated.rfind('!')
    last_question = truncated.rfind('?')
    
    # Find the last sentence ending
    last_sentence_end = max(last_period, last_exclamation, last_question)
    
    if last_sentence_end > max_chars * 0.8:  # If we can find a sentence end in the last 20%
      return text[:last_sentence_end + 1]
    else:
      return truncated + "..."
      
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
          print("key ====== ", key)
          presigned_url = self.aws_service.get_file(key)
          print("presigned_url ====== ", presigned_url)

          
          current_app.logger.info(f"File uploaded to S3: {filename}")

          try:
            # Use the pre-signed URL to extract text from the PDF
            text = self.resume_service.get_resume_pdf_text(file_url=presigned_url)
            current_app.logger.info(f"Text extracted from PDF: {filename}")
            
            print("text ====== ", text)
            
            # Truncate text to prevent context length exceeded error
            truncated_text = self._truncate_text_for_llm(text)
            current_app.logger.info(f"Text truncated from {len(text)} to {len(truncated_text)} characters for {filename}")
            
            prompt = parsed_resume_prompt(truncated_text)
            combined_prompt = f"{prompt}\n\n{truncated_text}" if truncated_text else prompt
            generated_text = self.llm_service.get_groq_response(prompt=combined_prompt)
            
            # Extract JSON from the LLM response
            extracted_json = self._extract_json_from_response(generated_text)
            if extracted_json:
              generated_text = extracted_json

            self.resume_service.create_resume(filename=filename, file_key=key, ai_text=generated_text, text=text, user_id=user['id'])
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

  def generate_resume(self):
    if request.method == 'POST':
      # Collect form data
      personal_info = {
        'name': request.form.get('name'),
        'email': request.form.get('email'),
        'phone': request.form.get('phone'),
        'linkedin': request.form.get('linkedin'),
        'github': request.form.get('github')
      }
      
      # Handle multiple work experiences
      work_experiences = []
      work_exp_count = int(request.form.get('work_exp_count', 0))
      for i in range(work_exp_count):
        work_exp = {
          'position': request.form.get(f'position_{i}'),
          'company': request.form.get(f'company-name_{i}'),
          'description': request.form.get(f'description_{i}', '').split('\n')
        }
        work_experiences.append(work_exp)
      
      # Handle multiple projects
      projects = []
      project_count = int(request.form.get('project_count', 0))
      for i in range(project_count):
        project = {
          'name': request.form.get(f'project_name_{i}'),
          'description': request.form.get(f'project_description_{i}', '').split('\n')
        }
        projects.append(project)
      
      skills = request.form.get('skills', '').split(',')
      
      education = {
        'degree': request.form.get('degree'),
        'institution': request.form.get('institution'),
        'year': request.form.get('graduation-year'),
        'gpa': request.form.get('gpa')
      }
      
      data = {
        'personal_info': personal_info,
        'work_experiences': work_experiences,
        'projects': projects,
        'skills': skills,
        'education': education
      }
    
      return render_template('resume.html', data=data)
    return render_template('resume.html', data={})