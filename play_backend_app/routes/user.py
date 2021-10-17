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
    return send_from_directory(os.path.join(app.root_path, 'uploads'), filename=filename)

@app.route('/upload', methods=['GET', 'POST'])
def uploadfile():
    if request.method == 'POST':
        print(request.headers)
        file = request.files.get('file')
        if not file or file.filename == '': 
            return jsonify({
                'error': True,
                'message': 'File not present.'
            })
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            try:
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            except:
                os.mkdir(app.config['UPLOAD_FOLDER'])
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        fileUrl = url_for('downloadFile', filename=filename)
        # Update the url for the saved image in the database
        
        return jsonify({
            'error': False,
            'fileUrl': fileUrl,
            'message': 'Image Updated successfully.'
        })
    else:
        return jsonify({
            'error': True,
            'message': 'Invalid request method.'
        })
