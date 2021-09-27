from play_backend_app import app
from flask import render_template, jsonify

@app.route('/')
def home():
	return render_template('home.html')

@app.route('/info')
def appInfo():
	return jsonify({
		'error': False,
  		'allSystemsWorkingFine': True,
  		'version': '0.0.2',
		'name': 'play-backend-app',
  		'author': 'Kushagra Bainsla',
		'Description': 'RESTful API endpoints and backend service for play.',
		'routes': {
			'public': 3,
			'protected': 9,
      	},
		'sockets': 2,
	})
