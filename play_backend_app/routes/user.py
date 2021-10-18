import os
from play_backend_app import app
from .. import db
from flask import request, jsonify, url_for, send_from_directory
from werkzeug.utils import secure_filename

# ( GET REQUEST ) For getting user's profile details.
@app.route('/user/profile')
def profile():
    if request.method == 'GET':
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
@app.route('/user/connections')
def allConnections():
    if request.method == 'GET':
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
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploads/<filename>')
def downloadFile(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename=filename)

@app.route('/user/update', methods=['PUT'])
def uploadfile():
    if request.method == 'PUT':
        if request.headers.get('Authorization'):
            tokenType, token = request.headers.get('Authorization').split()
            userID = request.headers.get('userID')
            
            if tokenType != 'Bearer': return 'Wrong token type.'
            if not token or token != os.environ.get('SECRET_TOKEN'): return 'Invalid Token.'
            if not userID: return 'Invalid User ID.' 

            newUserName, newUserBio, newUserGender, newUserPhotoURL = False, False, False, False

            if request.form.get('userName'): newUserName = request.form.get('userName')
            if request.form.get('userBio'): newUserBio = request.form.get('userBio')

            file = request.files.get('userImage')
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                try:
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                except:
                    os.mkdir(app.config['UPLOAD_FOLDER'])
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                newUserPhotoURL = 'http://play-backend-app.herokuapp.com' + url_for('downloadFile', filename=filename)

            
            profiles = db.user_profiles
            profile = profiles.find_one({"_id": str(userID)})
            if profile:
                userName = newUserName if newUserName else profile['details']['userName']
                userGender = newUserGender if newUserGender else profile['details']['userGender']
                userPhotoURL = newUserPhotoURL if newUserPhotoURL else profile['details']['userPhotoURL']
                profiles.update_one(
                    {"_id": str(userID)},
                    {"$set":
                        {
                            'details': {
                                'userId': userID,
                                'userName': userName,
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
