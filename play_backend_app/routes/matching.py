import os
from typing import Collection
from play_backend_app import app, db
from flask import request, jsonify

# ( GET REQUEST ) For finding matches for given userID and updating it in Database.
# This will be called when the user refresh the feed.
@app.route('/v1/makeMatches')
def makeMatches():
    if request.headers.get('Authorization'): 
    
        tokenType, token = request.headers.get('Authorization').split()
        userID = request.headers.get('userID')

        if tokenType != 'Bearer':
            return jsonify({
                'error': True,
                'message' : 'Invalid Token Type' 
            })
        if not token or token != os.environ.get('SECRET_TOKEN'):
            return jsonify({
                'error': True,
                'message' : 'Invalid Token.' 
            })
        if not userID: 
            return jsonify({
                'error': True,
                'message' : 'Invalid User ID.' 
            })
        
        profiles = db.user_profiles
        connections = db.user_connections
        my_profile = profiles.find_one({"_id": userID})
            
        def are_similar(unique_char1, unique_char2):
            match_score, basis = 0, {}
            for char1, value1 in unique_char1.items():
                for char2, value2 in unique_char2.items():
                    if char1 == char2:
                        match_score += min(value1, value2)
                        basis[char1] = min(value1, value2)

            if match_score > 0: return basis
            else: return False

        newConnections = []
        for other_profile in profiles.find():
            if other_profile['_id'] != userID:
                res = are_similar(my_profile['likes'], other_profile['likes'])
                if res:
                    newConnections.append({
                        'user_id': other_profile['_id'],
                        'matched_likes': res
                    })

        isUserPresent = connections.find_one({'_id': userID})  
        if isUserPresent:
            myQuery = {'_id': userID}
            newValues = {'$set': {'connections': newConnections}}
            connections.update_one(myQuery, newValues)
        else:
            connections.insert_one({
                '_id': str(userID),
                'connections': newConnections,
            })

        return jsonify({
            'error': False,
            'result': {
                'userID' : userID,
                'token' : os.environ.get("SECRET_TOKEN"),
            }
        })

    else:
        return jsonify({
            'error': True,
            'message' : 'Invalid request method.' 
        })
