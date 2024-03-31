import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = os.getenv('MAIL_PORT')
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    DB_SERVER = os.environ.get('DB_SERVER')
    DB_NAME = os.environ.get('DB_NAME')
    DB_USERNAME = os.environ.get('DB_USERNAME')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    DB_DRIVER = os.environ.get('DB_DRIVER')
    BLOB_ACCOUNT_NAME = os.environ.get('BLOB_ACCOUNT_NAME')
    BLOB_ACCOUNT_KEY = os.environ.get('BLOB_ACCOUNT_KEY')
    BLOB_CONTAINER = os.environ.get('BLOB_CONTAINER')