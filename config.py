import os

class Config:
  GROQ_API_KEY = os.getenv('GROQ_API_KEY')
  UPLOAD_FOLDER = 'uploads/'
  ALLOWED_EXTENSIONS = {'pdf'}
  SECRET_KEY = os.getenv('SECRET_KEY') | 'secret_key'
  SESSION_TYPE = 'filesystem'
  SESSION_COOKIE_NAME = os.getenv('SESSION_COOKIE_NAME') | 'your_session_cookie_name'
  SESSION_COOKIE_HTTPONLY = True
  SESSION_COOKIE_SECURE = True
  SESSION_COOKIE_MAX_SIZE = 4093

class DevelopmentConfig(Config):
  DEVELOPMENT = True
  DEBUG = True

config = {
  "development": DevelopmentConfig,
}