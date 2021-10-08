import os
import collections
from play_backend_app import app, db
from flask import request, jsonify

# This is called when a user log in, whether new user or old user, doesn't matter
@app.route('/login', methods = ['GET', 'POST'])
def userLogin():
    if request.method == 'POST':
        peopleResponse, youtubeResponse = request.json['peopleResponse']['result'], request.json['youtubeResponse']['result']
        userID, userName, userGender, userPhotoURL = '', '', '', ''

        for key, val in peopleResponse.items():
            if key == 'names':
                userName = val[0]['displayName']
                metadata = val[0]['metadata']
                source = metadata['source']
                userID = source['id']

            if key == 'photos':
                userPhotoURL = val[0]['url']
            if key == 'genders':
                userGender = val[0]['formattedValue']

        userLikes = []
        for data in youtubeResponse['items']:
            data_snippet = data['snippet']
            for key, val in data_snippet.items():
                if key == 'title':
                    if val != 'Deleted video': userLikes.append(val)


        # Generating a unique list of words of a user by his/her liked videos    
        meaningless_words = ['a', 'as', 'by', 'top', 'an', 'the', 'in', 'of', 'for', 'to', 'and', 'is', 'that', 'will', 'your', 'me', 'if', 'you', 'can', 'let', 'from', 'why', 'who',
                            'he', 'she', 'it', 'they', 'with', 'not', 'does', 'being', 'no', 'how', 'so', 'took', 'do', 'get', 'on', 'we', 'put', 'be', 'at', 'than', 'this', 'then', 'using', '']
        unique_list = []
        for like in userLikes:
            li = list(like.split())
            for letter in li:
                if letter.isalpha() and letter.lower() not in meaningless_words:
                    unique_list.append(letter)

        # The decluttered COUNTER of words og User's liked-videos playlist.
        declutteredUserLikes = dict(collections.Counter(unique_list))


        profiles = db.user_profiles
        # If user already present, just update details and likes.
        if profiles.find_one({"_id": str(userID)}):
            profiles.update_one(
                { '_id': str(userID) },
                { '$set': {
                    'details': {
                        'userId': userID,
                        'userName': userName,
                        'userGender': userGender,
                        'userPhotoURL': userPhotoURL,
                    },
                    'likes': declutteredUserLikes,
                }}
            )

        else:  # Else, add user.
            profiles.insert_one({
                '_id': str(userID),
                'details': {
                    'userId': userID,
                    'userName': userName,
                    'userGender': userGender,
                    'userPhotoURL': userPhotoURL,
                },
                'likes': declutteredUserLikes,
                'socials': {
                    'instagram': '',
                    'facebook': '',
                    'twitter': '',
                    'snapchat': '',
                    'linkedin': '',
                }
            })

        return jsonify({
            'error': False,
            'result': {
                'userID' : userID,
                'token' : os.environ.get("SECRET_TOKEN"),
            }
        })
    return jsonify({
        'error': True,
        'errorMessage': 'Invalid request method.',
    })