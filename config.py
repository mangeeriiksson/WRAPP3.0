import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'data', 'WRAPP.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
