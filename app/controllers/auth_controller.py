import bcrypt
from flask import render_template, redirect, url_for, session

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

  return redirect(url_for('app.dashboard'))

def signup(name, email, password):
  user = get_user_email(email)
  if user:
    session['signup_error'] = "User already exists. Please try a different email."
    return redirect(url_for('auth.signup'))
  
  hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

  create_user(name=name,email=email,password=hashed_password)
  
  return redirect(url_for('app.dashboard'))
