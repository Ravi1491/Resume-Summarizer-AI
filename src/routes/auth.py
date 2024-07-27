from flask import Blueprint
from .index import token_required
from ..controllers.auth_controller import AuthController

auth = Blueprint('auth', __name__)
auth_controller = AuthController()

@auth.route('/login', methods=['POST','GET'])
def login():
  return auth_controller.login()

@auth.route('/signup', methods=['POST','GET'])
def signup():
  return auth_controller.signup()

@auth.route('/logout', methods=['POST'])
@token_required
def logout():
  return auth_controller.logout()