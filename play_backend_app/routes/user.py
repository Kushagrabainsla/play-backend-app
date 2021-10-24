import os
from .. import app, db, bucket
from flask import request, jsonify, url_for, send_from_directory
from werkzeug.utils import secure_filename

# ( GET REQUEST ) For getting user's profile details.
@app.route('/v1/user/profile')
def profile():
    if request.method == 'GET':
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
            res = profiles.find_one({"_id": str(userID)})
            if res:
                return jsonify({
                    'error': False,
                    'result': res
                })
            else: 
                return jsonify({
                    'error': True,
                    'message' : 'User not Found.' 
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

# ( GET REQUEST ) For getting user's connections.
@app.route('/v1/user/connections')
def allConnections():
    if request.method == 'GET':
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
                        'message' : 'Connections not Found.' 
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




def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    if '.' in filename:
        extension = filename.split('.')[-1]
        if extension.lower() in ALLOWED_EXTENSIONS: return True
    return False

# ( PUT REQUEST ) For updating user's proflie
@app.route('/v1/user/update', methods=['PUT'])
def uploadfile():
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

            newUserName, newUserBio, newUserGender, newUserPhotoURL = False, False, False, False

            if request.form.get('userName'): newUserName = request.form.get('userName')
            if request.form.get('userBio'): newUserBio = request.form.get('userBio')

            file = request.files.get('userImage')
                
            if file and allowed_file(file.filename):
                extension = file.filename.split('.')[-1]
                newFilename = userID + '.' + extension
                blob = bucket.blob('userProfilePhoto/' + newFilename)
                blob.upload_from_file(file)
                blob.make_public()
                newUserPhotoURL = blob.public_url

            profiles = db.user_profiles
            profile = profiles.find_one({"_id": str(userID)})
            if profile:
                userName = newUserName if newUserName else profile['details']['userName']
                userBio = newUserBio if newUserBio else profile['details']['userBio']
                userGender = newUserGender if newUserGender else profile['details']['userGender']
                userPhotoURL = newUserPhotoURL if newUserPhotoURL else profile['details']['userPhotoURL']
                profiles.update_one(
                    {"_id": str(userID)},
                    {"$set":
                        {
                            'details': {
                                'userId': userID,
                                'userName': userName,
                                'userBio': userBio,
                                'userGender': userGender,
                                'userPhotoURL': userPhotoURL,
                            },
                        }
                    }
                )
            
            return jsonify({
                'error': False,
                'message': 'Profile Updated successfully.'
            })
        else:
            return jsonify({
                'error': True,
                'message' : 'Invalid authorization.' 
            })
    else:
        return jsonify({
            'error': True,
            'message': 'Invalid request method.'
        })

