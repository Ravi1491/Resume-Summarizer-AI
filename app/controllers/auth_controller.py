import bcrypt
from flask import redirect, url_for, session
from datetime import datetime, timedelta
import jwt
from ..models import get_user_email,create_user

def login(email, password):
  user = get_user_email(email)
  if not user:
    session['login_error'] = "User not found"
    return redirect(url_for('auth.login'))

  is_valid = bcrypt.checkpw(password.encode('utf-8'), user[3])
  
  if not is_valid:
    session['login_error'] = "Invalid password"
    return redirect(url_for('auth.login'))
  
  session['logged_in'] = True
  token = jwt.encode({
    'id': user[0],
    'email': email,
    'exp': datetime.utcnow() + timedelta(hours=24)
  }, 'SECRET_KEY', algorithm='HS256')
  
  session['token'] = token

  return redirect(url_for('dashboard.home'))

def signup(name, email, password):
  user = get_user_email(email)
  if user:
    session['signup_error'] = "User already exists. Please try a different email."
    return redirect(url_for('auth.signup'))
  
  hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

  create_user(name=name,email=email,password=hashed_password)
  new_uer = get_user_email(email)

  session['logged_in'] = True
  token = jwt.encode({
    'id': new_uer[0],
    'email': email,
    'exp': datetime.utcnow() + timedelta(hours=24)
  }, 'SECRET_KEY', algorithm='HS256')
  
  session['token'] = token

  return redirect(url_for('dashboard.home'))

def logout():
  session.clear()
  return redirect(url_for('auth.login'))