import jwt
from datetime import datetime, timedelta

class TokenService():
  def __init__(self, secret_key='SECRET_KEY', algorithm='HS256') -> None:
    self.secret_key = secret_key
    self.algorithm = algorithm
  
  def generate_token(self, user):
    return jwt.encode({
      'id': user[0],
      'email': user[2],
      'exp': datetime.utcnow() + timedelta(hours=24)
    }, self.secret_key, algorithm=self.algorithm)
    