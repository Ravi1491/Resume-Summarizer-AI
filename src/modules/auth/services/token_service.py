import jwt
from datetime import datetime, timedelta

class TokenService():
  def __init__(self, secret_key='SECRET_KEY', algorithm='HS256') -> None:
    self.secret_key = secret_key
    self.algorithm = algorithm
  
  
  def generate_token(self, id, email):
    return jwt.encode({
      'id': id,
      'email': email,
      'exp': datetime.utcnow() + timedelta(hours=24)
    }, self.secret_key, algorithm=self.algorithm)
    
  def decode_token(self, token):
    return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])