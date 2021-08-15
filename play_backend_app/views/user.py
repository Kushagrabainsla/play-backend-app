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
        # In production .env file is not uploaded to github so can't get token from env file
        # DO SOMETHING ABOUT IT !!
        # if not token or token != os.getenv('SECRET_TOKEN'): return 'Invalid Token.'
        if not token or token != 'blruvyq362f3t9746rbvt578tbcr367b48br34t786fg47985nt27v54': return 'Invalid Token.'
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
        # if not token or token != os.getenv('SECRET_TOKEN'): return 'Invalid Token.'
        if not token or token != 'blruvyq362f3t9746rbvt578tbcr367b48br34t786fg47985nt27v54': return 'Invalid Token.'
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
