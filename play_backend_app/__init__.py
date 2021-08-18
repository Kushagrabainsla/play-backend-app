import os
from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)

client = MongoClient(os.environ("MONGO_CLIENT_ID"))
db = client.user_database

from .views import *
