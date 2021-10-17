import os
import logging
from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
from flask_socketio import SocketIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


# Logger
logging.basicConfig(filename='error.log')

app = Flask(__name__)
# app.config['UPLOAD_FOLDER'] = './play_backend_app/uploads'
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
