from play_backend_app import app
from flask import render_template

@app.route('/')
def home():
	return render_template('home.html')

@app.route('/error')
def error():
	return render_template('error.html')
