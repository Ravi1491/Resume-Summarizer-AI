import os
from dotenv import load_dotenv

load_dotenv()

class Config:
  GROQ_API_KEY = os.getenv('GROQ_API_KEY')
  CONFIG_MODE = os.getenv('CONFIG_MODE')
  SQLALCHEMY_DATABASE_URI= os.getenv('SQLALCHEMY_DATABASE_URI')
  SQLALCHEMY_MIGRATE_REPO = os.path.join(os.path.dirname(__file__), 'database', 'migrations')
  SQLALCHEMY_TRACK_MODIFICATIONS = False
  ALLOWED_EXTENSIONS = {'pdf'}
  SECRET_KEY = os.getenv('SECRET_KEY') or 'secret_key'
  SESSION_TYPE = 'filesystem'
  SESSION_COOKIE_NAME = os.getenv('SESSION_COOKIE_NAME') or 'your_session_cookie_name'
  SESSION_COOKIE_HTTPONLY = True
  SESSION_COOKIE_SECURE = True
  SESSION_COOKIE_MAX_SIZE = 4093
  AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
  AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
  AWS_REGION = os.getenv('AWS_REGION')
  AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')
  LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
  LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT")
  LANGCHAIN_TRACING_V2 = "true"


class DevelopmentConfig(Config):
  DEBUG = True

class ProductionConfig(Config):
  DEBUG = False
