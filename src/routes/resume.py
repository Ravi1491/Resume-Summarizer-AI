from flask import Blueprint

from .index import token_required
from ..modules.resume.controllers.resume_controller import ResumeController

resume = Blueprint('resume', __name__)
resume_controller = ResumeController()

@resume.route('/dashboard')
@token_required
def home():
  return resume_controller.home()

@resume.route('/compare-resume', methods=['POST', 'GET'])
@token_required
def compare():
  return resume_controller.compare_resume_with_job()

@resume.route('/view/<int:id>')
@token_required
def view_pdf(id):
  return resume_controller.get_resume_summary(id=id)

@resume.route('/delete/<int:id>', methods=['POST'])
@token_required
def delete_pdf(id):
  return resume_controller.delete_resume(id=id)

@resume.route('/upload', methods=['POST'])
@token_required
def upload_file():
  return resume_controller.upload_resume()