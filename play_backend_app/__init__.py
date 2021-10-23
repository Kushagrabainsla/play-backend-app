import os
import logging
from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
from flask_socketio import SocketIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from firebase_admin import credentials, initialize_app, storage

credentialJsonDict = {
    "type": "service_account",
    "project_id": "play0-1",
    "private_key_id": os.environ.get("FIREBASE_PRIVATE_KEY_ID"),
    "private_key": os.environ.get("FIREBASE_PRIVATE_KEY"),
    "client_email": "play0-1@appspot.gserviceaccount.com",
    "client_id": os.environ.get("FIREBASE_CLIENT_ID"),
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/play0-1%40appspot.gserviceaccount.com"
}

# Firebase Bucket
cred = credentials.Certificate(credentialJsonDict)
initialize_app(cred, {'storageBucket': 'play0-1.appspot.com'})
bucket = storage.bucket()


# Logger
logging.basicConfig(filename='error.log')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
socket = SocketIO(app, cors_allowed_origins="*")
CORS(app)

# Additional rate limiter
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["30 per minute"]
)

client = MongoClient(os.environ.get("MONGO_CLIENT_ID"))
db = client['user_database']


from .routes import *
