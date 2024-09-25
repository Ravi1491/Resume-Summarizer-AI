import jwt
from functools import wraps

from flask import Blueprint, render_template, session, redirect, url_for
from ..modules.auth.services.user_service import UserService

app = Blueprint('app', __name__)

def token_required(fun):
  @wraps(fun)
  def decorated(*args, **kwargs):
    token = session.get('token')
    if not token:
      return redirect(url_for('auth.login'))
    try:
      payload = jwt.decode(token, 'SECRET_KEY', algorithms=['HS256'])
      user = UserService.get_user_by_email(payload.get('email'))
      if not user:
        return redirect(url_for('auth.login'))
      session['user'] = payload
    except jwt.ExpiredSignatureError:
        session.clear()
        return redirect(url_for('auth.login'))
    except jwt.InvalidTokenError:
        session.clear()
        return redirect(url_for('auth.login'))

    except:
      return redirect(url_for('auth.login'))
    return fun(*args, **kwargs)

  return decorated

@app.route('/health')
def health():
    return 'OK'

@app.route('/')
def index():
    return render_template('index.html')
