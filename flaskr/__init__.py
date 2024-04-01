from flask import Flask
from config import Config
from flask_mail import Mail
from flask_login import LoginManager
import pyodbc
from azure.storage.blob import BlobServiceClient

app = Flask(__name__)
app.config.from_object(Config)
conn = pyodbc.connect(f'SERVER={Config.DB_SERVER};DATABASE={Config.DB_NAME};UID={Config.DB_USERNAME};PWD={Config.DB_PASSWORD};DRIVER={Config.DB_DRIVER}')
login = LoginManager(app)
login.login_view = 'login'
blob_service_client = BlobServiceClient.from_connection_string(Config.BLOB_CONN_STR)
blob_container = Config.BLOB_CONTAINER

mail = Mail(app)

from flaskr import routes