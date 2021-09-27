import os
from play_backend_app import app
from .. import db
from flask import request, jsonify

# ( GET REQUEST ) For getting user's profile details.
@app.route('/user/profile')
def profile():
    if request.headers.get('Authorization'): 
        tokenType, token = request.headers.get('Authorization').split()
        userID = request.headers.get('userID')
        
        if tokenType != 'Bearer': return 'Wrong token type.'
        if not token or token != os.environ.get('SECRET_TOKEN'): return 'Invalid Token.'
        if not userID: return 'Invalid User ID.'
            
        profiles = db.user_profiles
        res = profiles.find_one({"_id": str(userID)})
        if res:
            return jsonify({
                'error': False,
                'result': res
            })
        else: 
            return jsonify({
                'error': True,
                'message' : 'User not Found !!' 
            })
    else:
        return 'Access denied.'

# ( GET REQUEST ) For getting user's connections.
@app.route('/user/connections')
def allConnections():
    if request.headers.get('Authorization'): 
        tokenType, token = request.headers.get('Authorization').split()
        userID = request.headers.get('userID')
        
        if tokenType != 'Bearer': return 'Wrong token type.'
        if not token or token != os.environ.get('SECRET_TOKEN'): return 'Invalid Token.'
        if not userID: return 'Invalid User ID.'

        connections = db.user_connections
        res = connections.find_one({"_id": str(userID)})
        if res:
            return jsonify({
                    'error': False,
                    'result': res['connections']
                })
        else:
            return jsonify({
                    'error': True,
                    'message' : 'Connections not Found !!' 
                })
    else:
        return 'Access denied.'
