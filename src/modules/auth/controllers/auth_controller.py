from flask import redirect, url_for, session, request,render_template
from ..services.user_service import UserService
from ..services.password_service import PasswordService
from ..services.token_service import TokenService

class AuthController:
  def __init__(self):
    self.user_service = UserService()
    self.password_service = PasswordService()
    self.token_service = TokenService()
    
  def login(self):
    if session.get('logged_in'):
      return redirect(url_for('resume.home'))
    
    if request.method == 'POST':
      try:
        email = request.form['email']
        password = request.form['password']
        
        user = self.user_service.get_user_by_email(email)
        if not user:
          session['login_error'] = "User not found"
          return redirect(url_for('auth.login'))
        
        if not self.password_service.check_password(password, user[3]):
          session['login_error'] = "Invalid password"
          return redirect(url_for('auth.login'))
        
        session['logged_in'] = True
        token = self.token_service.generate_token(user)
        session['token'] = token
        
        return redirect(url_for('resume.home'))
      except Exception as e:
        session['login_error'] = f"An error occurred: {str(e)}"
        return redirect(url_for('auth.login'))
        
    error = session.pop('login_error', None)
    return render_template('login.html', error=error)
  
  def signup(self):
    if session.get('logged_in'):
      return redirect(url_for('resume.home'))
    
    if request.method == 'POST':
      try:
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        if self.user_service.get_user_by_email(email):
          session['signup_error'] = "User already exists"
          return redirect(url_for('auth.signup'))
        
        hashed_password = self.password_service.hash_password(password)
        new_user = self.user_service.create_user(name, email, hashed_password)
        
        session['logged_in'] = True
        token = self.token_service.generate_token(new_user)
        session['token'] = token
        
        return redirect(url_for('resume.html'))
      
      except Exception as e:
        session['signup_error'] = f"An error occurred: {str(e)}"
        return redirect(url_for('auth.signup'))

    error = session.pop('signup_error', None)
    return render_template('signup.html', error=error)

  def logout(self):
    session.clear()
    return redirect(url_for('auth.login'))
