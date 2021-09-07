import os
from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
from flask_socketio import SocketIO


app = Flask(__name__)
app.config['SECRET_KEY'] = '45106758472ufg9vqrehvr7v9e8qvqhwe'
socket = SocketIO(app, cors_allowed_origins="*")
CORS(app)


client = MongoClient(os.environ.get("MONGO_CLIENT_ID"))
db = client['user_database']


from .views import *
