from flask import render_template, request, redirect, flash, url_for, Blueprint, current_app, session
from werkzeug.utils import secure_filename
from ..models import get_all_pdfs, delete_pdf_entry, get_pdf_by_id, get_resumes_by_user_id
from ..utils import get_resume_pdf_text, groq_response, allowed_file,match_job_description
import os
import sqlite3
import json
from ..utils import dict_to_html_table,resume_template
from .index import token_required

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/dashboard')
@token_required
def home():
  user = session.get('user')
  uploaded_pdfs = get_resumes_by_user_id(user_id=user['id'])
  return render_template('dashboard.html', uploaded_pdfs=uploaded_pdfs)

@dashboard.route('/compare-resume', methods=['POST', 'GET'])
@token_required
def compare():
  if request.method == 'POST' and 'job_description' in request.form:
    user = session.get('user')
    allPdfs = get_resumes_by_user_id(user_id=user['id'])
    final_res = []
        
    for pdf in allPdfs:
      res = match_job_description(file_name=pdf[1],ai_text=pdf[3], job_description=request.form['job_description'])
      santize_res = json.loads(res)
      final_res.append(santize_res)
        
    data = {
        'job_description': request.form['job_description'],
        'comparison_results': final_res
    }
    return render_template('compare.html', data=data)

  return render_template('compare.html')

@dashboard.route('/view/<int:id>')
@token_required
def view_pdf(id):
  pdf = get_pdf_by_id(id)
  if pdf:
    content = json.loads(pdf[2])
    html_table = dict_to_html_table(content)
    return render_template('view.html', pdf=html_table)
  else:
    flash('PDF not found')
    return render_template('fallback.html')
  
@dashboard.route('/generate-resume', methods=['GET', 'POST'])
def generate_resume():
  if request.method == 'GET':
    return render_template('resume.html', data={})

  description_points = ["Worked on various projects"]
  if len(request.form.get('description')) > 0:
    description_points = request.form.get('description').split('\n')
    description_points = [point.strip() for point in description_points if len(point.strip()) > 0]

  print(description_points)
  
  data = {
    "personnal_info": {
        "name": request.form.get('name') if len(request.form.get('name')) > 0 else "John Doe",
        "email": request.form.get('email') if len(request.form.get('email')) > 0 else "johnDoe@gmail.com",
        "phone": request.form.get('phone') if len(request.form.get('phone')) > 0 else "1234567890",
        "linkedin": request.form.get('linkedin') if len(request.form.get('linkedin')) > 0 else "linkedin.com/johndoe",
        "github": request.form.get('github') if len(request.form.get('github')) > 0 else "github.com/johndoe",
    },
    "work_experience": {
        "position": request.form.get('position') if len(request.form.get('position')) > 0 else "Software Developer",
        "company": request.form.get('company-name') if len(request.form.get('company-name')) > 0 else "ABC Company",
        "description": description_points,
    },
    "projects": {
      "name": request.form.get('project-name') if len(request.form.get('project-name')) > 0 else "Project 1",
      "link": request.form.get('project-link') if len(request.form.get('project-link')) > 0 else "project1.com",
      "description": request.form.get('project-description') if len(request.form.get('project-description')) > 0 else "Project Description",
    },
    "skills": request.form.get('skills') if len(request.form.get('skills')) > 0 else "",
  }

  # html = resume_template(data)
  return render_template('resume.html', data=data)

@dashboard.route('/delete/<int:id>', methods=['POST'])
@token_required
def delete_pdf(id):
  delete_pdf_entry(id)
  return redirect(url_for('dashboard.home'))

@dashboard.route('/upload', methods=['POST'])
@token_required
def upload_file():
  user = session.get('user')

  if 'pdfs' not in request.files:
    flash('No file part')
    return redirect(request.url)

  files = request.files.getlist('pdfs')

  for file in files:
    if file and allowed_file(file.filename):
      filename = secure_filename(file.filename)
      file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

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

      combined_prompt = f"{prompt}\n\n{text}" if text else prompt
      generated_text = groq_response(combined_prompt)

      with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO pdfs (filename, text, ai_text, user_id) VALUES (?,?,?,?)', (filename,text, generated_text,user['id'],))
        conn.commit()
    else:
      flash(f'File {file.filename} is not a valid PDF')

  return redirect(url_for('dashboard.home'))
