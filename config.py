import os
from dotenv import load_dotenv

load_dotenv()

class Config:
  GROQ_API_KEY = os.getenv('GROQ_API_KEY')
  CONFIG_MODE = os.getenv('CONFIG_MODE')
  UPLOAD_FOLDER = 'uploads/'
  ALLOWED_EXTENSIONS = {'pdf'}
  SECRET_KEY = os.getenv('SECRET_KEY') or 'secret_key'
  SESSION_TYPE = 'filesystem'
  SESSION_COOKIE_NAME = os.getenv('SESSION_COOKIE_NAME') or 'your_session_cookie_name'
  SESSION_COOKIE_HTTPONLY = True
  SESSION_COOKIE_SECURE = True
  SESSION_COOKIE_MAX_SIZE = 4093

class DevelopmentConfig(Config):
  DEBUG = True

class ProductionConfig(Config):
  DEBUG = False
