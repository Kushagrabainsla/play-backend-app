import os
from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)

# client = MongoClient(os.getenv("MONGO_CLIENT_ID"))
client = MongoClient('mongodb+srv://dbuser:dbuserpassword@cluster0.innvx.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.user_database

from .views import *
