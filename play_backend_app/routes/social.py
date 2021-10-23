import os
from play_backend_app import app, db
from flask import request, jsonify

@app.route('/updateSocials', methods = ['GET', 'PUT'])
def updateSocials():
    if request.method == 'PUT':
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
            
            newInstagram, newFacebook, newTwitter, newSnapchat, newLinkedin = False, False, False, False, False

            socialName = request.json['socialName']
            userHandle = request.json['userHandle']
            if socialName == 'Instagram': newInstagram = userHandle
            elif socialName == 'Facebook': newFacebook = userHandle
            elif socialName == 'Twitter': newTwitter = userHandle
            elif socialName == 'Snapchat': newSnapchat = userHandle
            elif socialName == 'Linkedin': newLinkedin = userHandle
            
            profiles = db.user_profiles
            profile = profiles.find_one({"_id": str(userID)})
            if profile:
                # If updated, use the updated value, else use previous value.
                instagram = newInstagram if newInstagram else profile['socials']['instagram']
                facebook = newFacebook if newFacebook else profile['socials']['facebook']
                twitter = newTwitter if newTwitter else profile['socials']['twitter']
                snapchat = newSnapchat if newSnapchat else profile['socials']['snapchat']
                linkedin = newLinkedin if newLinkedin else profile['socials']['linkedin']
                profiles.update_one(
                    {"_id": str(userID)},
                    {"$set":
                        {
                            "socials": {
                                'instagram': instagram,
                                'facebook': facebook,
                                'twitter': twitter,
                                'snapchat': snapchat,
                                'linkedin': linkedin,
                            }
                        }
                    }
                )
                return jsonify({
                    'error': False,
                    'message': 'Socials updated.'
                })
            return jsonify({
                'error': True,
                'errorMessage': 'No profile found.'
            })
        else:
            return jsonify({
                'error': True,
                'message' : 'Invalid authorization.' 
            })
    else:
        return jsonify({
            'error': True,
            'message' : 'Invalid request method.' 
        })
