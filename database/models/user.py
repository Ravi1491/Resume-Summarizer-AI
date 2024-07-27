from .. import db
from datetime import datetime
import bcrypt

class User(db.Model):
  __tablename__ = 'users'
  
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  name = db.Column(db.String(50), nullable=False)
  email = db.Column(db.String(50), nullable=False, unique=True)
  password = db.Column(db.String(100), nullable=False)
  created_at = db.Column(db.DateTime, default=datetime.utcnow)
  updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

  
  def __repr__(self):
    return f'<User {self.email}>'
  
  def __init__(self, name, email, password) -> None:
    self.name = name
    self.email = email
    self.password = password
    
  def set_password(self, password):
      """Hashes and sets the password for the user."""
      self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

  def check_password(self, password):
      """Checks if the provided password matches the user's hashed password."""
      return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
  
  def create_user_if_not_exists(self):
    db_user = User.query.filter(User.email == self.email).all()
    if not db_user:
      db.session.add(self)
      db.session.commit()

    return True
  
  def get_user_by_email(self):
    return User.query.filter(User.email == self.email).first()
  