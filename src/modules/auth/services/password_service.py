import bcrypt

class PasswordService():
  def hashed_password(self, password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
  
  def check_password(self, password, hashed_password):
    check = bcrypt.checkpw(password.encode('utf-8'), hashed_password)
    print(check)
    
    return check
    