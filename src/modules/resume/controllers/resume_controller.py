import os
from flask import session, render_template, current_app, request, json,redirect,url_for, flash
from werkzeug.utils import secure_filename
from ..services.resume_service import ResumeService
from ..services.groq_service import GroqService
from ..utils.prompt import genrate_html, match_job_description_prompt,parsed_resume_prompt

class ResumeController():
  def __init__(self) -> None:
    self.resume_service = ResumeService()
    self.groq_service = GroqService()
  
  def home(self):
    user = session.get('user')
    all_user_resumes = self.resume_service.get_reusme_by_user_id(user_id=user['id'])
    return render_template('dashboard.html', uploaded_pdfs = all_user_resumes)
  
  def compare_resume_with_job(self):
    if request.method == 'POST' and 'job_description' in request.form:
      if len(request.form['job_description']) == 0:
        flash('Job description cannot be empty.', 'error')
        return redirect(url_for('resume.home'))

      user = session.get('user')
      all_user_resumes = self.resume_service.get_reusme_by_user_id(user_id=user['id'])
      final_res = []
      
      for resume in all_user_resumes:
        prompt = match_job_description_prompt(file_name=resume[1],ai_text=resume[3], job_description=request.form['job_description'])
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
        content = json.loads(resume[2])
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
        return redirect(request.url)

      files = request.files.getlist('pdfs')
      for file in files:
        if file and self.resume_service.filter_file_by_extension(filename=file.filename):
          filename = secure_filename(file.filename)
          file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

          text = self.resume_service.get_resume_pdf_text(file=f'uploads/{filename}')
          prompt = parsed_resume_prompt(text)

          combined_prompt = f"{prompt}\n\n{text}" if text else prompt
          generated_text = self.groq_service.get_response(prompt=combined_prompt)

          self.resume_service.create_resume(filename=filename,ai_text=generated_text,text=text,user_id=user['id'])
        else:
          print(f'File {file.filename} is not a valid PDF')
      
      return redirect(url_for('resume.home'))
    except Exception as e:
      print(f"An error occurred: {str(e)}")
      return render_template(('dashboard.html'))
      