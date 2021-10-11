import os
import logging
from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
from flask_socketio import SocketIO

logging.basicConfig(filename='error.log')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
socket = SocketIO(app, cors_allowed_origins="*")
CORS(app)


client = MongoClient(os.environ.get("MONGO_CLIENT_ID"))
db = client['user_database']


from .routes import *
