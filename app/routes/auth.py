from flask import Blueprint, request, render_template, session

from ..controllers import auth_controller

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        return auth_controller.login(email=email, password=password)
    
    error = session.pop('login_error', None)
    return render_template('login.html', error=error)

@auth.route('/signup', methods=['POST','GET'])
def signup():
  if request.method == 'POST':
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    return auth_controller.signup(name=name, email=email, password=password)

  error = session.pop('signup_error', None)
  return render_template('signup.html',error=error)