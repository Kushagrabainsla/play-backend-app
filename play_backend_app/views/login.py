from play_backend_app import app
from flask import jsonify

@app.route('/login')
def userLogin():
    # Some behavior of this is based on /updateuser !!
    # Post on this endpoint when got all data
    # to save it in backend and return desired data.
    userID, token = 123, 'refreshedToken'

    return jsonify({
        'userID' : userID,
        'token' : token,
    })