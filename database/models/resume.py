from .. import db
from datetime import datetime

class Resume(db.Model):
  __tablename__ = 'resumes'
  
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  filename = db.Column(db.String(200), nullable=False)
  file_key = db.Column(db.String(), nullable=False)
  text = db.Column(db.Text, nullable=False)
  ai_text = db.Column(db.Text, nullable=False)
  user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
  created_at = db.Column(db.DateTime, default=datetime.utcnow)
  updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

  def __repr__(self):
    return f'<Resume {self.id}>'
  
  def __init__(self, filename, file_key, text, ai_text, user_id) -> None:
    self.filename = filename
    self.file_key = file_key
    self.text = text
    self.ai_text = ai_text
    self.user_id = user_id
  
  def to_dict(self):
    return {
      'id': self.id,
      'filename': self.filename,
      'file_key': self.file_key,
      'text': self.text,
      'ai_text': self.ai_text,
      'user_id': self.user_id,
    }