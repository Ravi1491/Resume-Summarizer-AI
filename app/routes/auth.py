from flask import Blueprint, request, render_template, session, request, jsonify, redirect, url_for
from .index import token_required
from ..controllers import auth_controller

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['POST','GET'])
def login():
    if session.get('logged_in'):
      return redirect(url_for('dashboard.home'))
  
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        return auth_controller.login(email=email, password=password)
    
    error = session.pop('login_error', None)
    return render_template('login.html', error=error)

@auth.route('/signup', methods=['POST','GET'])
def signup():
  if session.get('logged_in'):
    return redirect(url_for('dashboard.home'))

  if request.method == 'POST':
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    return auth_controller.signup(name=name, email=email, password=password)

  error = session.pop('signup_error', None)
  return render_template('signup.html',error=error)

@auth.route('/logout', methods=['POST'])
@token_required
def logout():
    return auth_controller.logout()