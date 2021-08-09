import os
from play_backend_app import app
from flask import request, jsonify
from .. import db

# ( PUT REQUEST ) For finding matches for given userID and updating it in DB.
# This will be called when the user refresh the feed.
@app.route('/findMatches')
def findMatches():
    if request.headers.get('Authorization'): 
    
        tokenType, token = request.headers.get('Authorization').split()
        userID = request.headers.get('userID')

        if tokenType != 'Bearer': return 'Wrong token type.'
        if not token: return 'Invalid Token.' # Verify the token
        if not userID: return 'Invalid User ID.'
        
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
                        "user_id": other_profile['_id'],
                        "matched_likes": res
                    })

        myQuery = {"_id": userID}
        newValues = {"$set": {"connections": newConnections}}
        connections.update_one(myQuery, newValues)

        return jsonify({
            'error': False,
            'result': {
                'userID' : userID,
                'token' : os.getenv("SECRET_TOKEN"),
            }
        })

    else:
        return 'Access denied.'
