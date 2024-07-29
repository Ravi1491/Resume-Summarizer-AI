from .. import db
from datetime import datetime

class User(db.Model):
  __tablename__ = 'users'
  
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  name = db.Column(db.String(50), nullable=False)
  email = db.Column(db.String(50), nullable=False, unique=True)
  password = db.Column(db.LargeBinary, nullable=False)
  created_at = db.Column(db.DateTime, default=datetime.utcnow)
  updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
  
  def __repr__(self):
    return f'<User id={self.id}, name={self.name}, email={self.email}, password={self.password}>'

  
  def __init__(self, name, email, password) -> None:
    self.name = name
    self.email = email
    self.password = password
    