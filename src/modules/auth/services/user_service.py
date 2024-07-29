from database.models.user import User
from database import db

class UserService():
  @staticmethod
  def get_user_by_email(email) -> User:
    user = User.query.filter(User.email == email).first()
    return user.to_dict() if user else None

  @staticmethod
  def create_user(name,email,password):
    user = User(name,email,password)
    db.session.add(user)
    db.session.commit()
    
    return user