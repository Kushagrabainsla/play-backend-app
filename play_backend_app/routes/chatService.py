import os
from flask import jsonify, request
from flask_socketio import emit
from .. import app, socket, db, limiter


@app.route('/socket/socketStatus')
def socketStatus():
    return jsonify({
        'error': False,
        'message': 'Sockets are working fine.'
    })


def addRoomIfNotPresent(room):
    # Pointer to the userRooms collections
    userRooms = db.user_rooms

    # Pointer to the array of chatrooms.
    chatRoomDocument = userRooms.find_one({'_id': 'chatRooms'}) 
    chatRooms = chatRoomDocument['chatRooms']

    if room not in chatRooms:
        userRooms.find_one_and_update({'_id': 'chatRooms'}, {'$push': {'chatRooms': room}})


def fetchRoomsFromDatabase():
    # Pointer to the userRooms collections
    userRooms = db.user_rooms

    # Pointer to the array of chatrooms.
    chatRoomDocument = userRooms.find_one({'_id': 'chatRooms'})
    chatRooms = chatRoomDocument['chatRooms']
        
    return jsonify({
        'error': False,
        'message': chatRooms,
    })
    

def addMessage(data):
    userMessages = db.user_messages
    
    room = data['room']
    roomPresent = userMessages.find_one({ '_id': room })
    
    # If room already present, just push the message
    if roomPresent:
        userMessages.find_one_and_update({ '_id': room }, { '$push': { 'messages': data } })
    # Else, create a new key-value pair.
    else:
        userMessages.insert_one({
            '_id': room,
            'messages': [ data ],
        })
        

def addChatInfo(data):
    profiles = db.user_profiles
    userChatInfo = db.user_chat_info

    authorId = data['author']
    receiverId = data['receiver']

    author = profiles.find_one({"_id": str(authorId)})
    receiver = profiles.find_one({"_id": str(receiverId)})
    
    authorPhotoUrl = author['details']['userPhotoURL']
    authorName = author['details']['userName']
    
    receiverPhotoUrl = receiver['details']['userPhotoURL']
    receiverName = receiver['details']['userName']
    
    messageBody = data['body']
    messageTimestamp = data['timeStamp']
    

    authorPresent = userChatInfo.find_one({'_id': authorId}) 
    if authorPresent:
        chatInfoArray = authorPresent['chatInfo']
        receiverInAuthorChats = False
        for chatIndex in range(len(chatInfoArray)):
            if chatInfoArray[chatIndex]['userId'] == receiverId:
                receiverInAuthorChats = True
                # Just update the info
                chatInfoArray[chatIndex] = {
                    'userId': receiverId,
                    'username': receiverName,
                    'userProfilePhoto': receiverPhotoUrl,
                    'lastMessageText': messageBody,
                    'lastMessageTimestamp': messageTimestamp,
                    'lastMessageSeen': True,
                }
                # Update the array in the database.
                userChatInfo.update_one(
                    { '_id': authorId },
                    {
                        '$set': {
                            'chatInfo': chatInfoArray
                        }
                    }
                )
                break
                
        if not receiverInAuthorChats:
            newChat = {
                'userId': receiverId,
                'username': receiverName,
                'userProfilePhoto': receiverPhotoUrl,
                'lastMessageText': messageBody,
                'lastMessageTimestamp': messageTimestamp,
                'lastMessageSeen': True,
            }
            userChatInfo.find_one_and_update({'_id': authorId}, {'$push': {'chatInfo': newChat}})
    else:
        userChatInfo.insert_one({
            '_id': authorId,
            'chatInfo': [
                {
                    'userId': receiverId,
                    'username': receiverName,
                    'userProfilePhoto': receiverPhotoUrl,
                    'lastMessageText': messageBody,
                    'lastMessageTimestamp': messageTimestamp,
                    'lastMessageSeen': True,
                }
            ]
        })

    receiverPresent = userChatInfo.find_one({'_id': receiverId}) 
    if receiverPresent:
        chatInfoArray = receiverPresent['chatInfo']
        authorInReceiverChats = False
        for chatIndex in range(len(chatInfoArray)):
            if chatInfoArray[chatIndex]['userId'] == authorId:
                authorInReceiverChats = True
                # Just update the info
                chatInfoArray[chatIndex] = {
                    'userId': authorId,
                    'username': authorName,
                    'userProfilePhoto': authorPhotoUrl,
                    'lastMessageText': messageBody,
                    'lastMessageTimestamp': messageTimestamp,
                    'lastMessageSeen': False,
                }
                # Update the array in the database.
                userChatInfo.update_one(
                    { '_id': receiverId },
                    {
                        '$set': {
                            'chatInfo': chatInfoArray
                        }
                    }
                )
                break

        if not authorInReceiverChats:
            newChat = {
                'userId': authorId,
                'username': authorName,
                'userProfilePhoto': authorPhotoUrl,
                'lastMessageText': messageBody,
                'lastMessageTimestamp': messageTimestamp,
                'lastMessageSeen': False,
            }
            userChatInfo.find_one_and_update({'_id': receiverId}, {'$push': {'chatInfo': newChat}})
    else:
        userChatInfo.insert_one({
            '_id': receiverId,
            'chatInfo': [
                {
                    'userId': authorId,
                    'username': authorName,
                    'userProfilePhoto': authorPhotoUrl,
                    'lastMessageText': messageBody,
                    'lastMessageTimestamp': messageTimestamp,
                    'lastMessageSeen': False,
                }
            ]
        })

def refreshedChatInfo(chatInfo):
    profiles = db.user_profiles
    for chat in chatInfo:
        chatProfile = profiles.find_one({'_id': chat['userId']}) 
        chat['userProfilePhoto'] = chatProfile['details']['userPhotoURL']
        chat['username'] = chatProfile['details']['userName']
    return chatInfo
    
@app.route('/v1/socket/markMessage', methods=['GET', 'PUT'])
@limiter.exempt
def markMessage():
    if request.method == 'PUT' and request.headers.get('Authorization'):
        if not request.headers.get('authorId'): return 'No Author sent.'
        if not request.headers.get('receiverId'): return 'No receiver sent.'
        
        tokenType, token = request.headers.get('Authorization').split()
        authorId = request.headers.get('authorId')
        receiverId = request.headers.get('receiverId')

        if tokenType != 'Bearer': return 'Wrong token type.'
        if not token or token != os.environ.get('SECRET_TOKEN'): return 'Invalid Token.'
        if not authorId: return 'Invalid Author.'
        if not receiverId: return 'Invalid Receiver.'

        # print('AuthorId:', authorId) # CLIENT 2
        # print('ReceiverId:', receiverId) # CLIENT 1
        userChatInfo = db.user_chat_info
        authorPresent = userChatInfo.find_one({'_id': authorId}) 
        if authorPresent:
            chatInfoArray = authorPresent['chatInfo']
            for chatIndex in range(len(chatInfoArray)):
                if chatInfoArray[chatIndex]['userId'] == receiverId:
                    # Just update the info
                    chatInfoArray[chatIndex]['lastMessageSeen'] = True
                    
                    # Update the array in the database.
                    userChatInfo.update_one(
                        { '_id': authorId },
                        { '$set': { 'chatInfo': chatInfoArray } }
                    )
                    break
        
        return jsonify({
            'error': False,
            'message': 'Chat info updated',
        })
    else:
        return jsonify({
            'error': True,
            'message': 'Access Denied.',
        })

# ----------------------------------------------------------------------------------------------------


@app.route('/v1/socket/chats')
@limiter.exempt
def fetchChats():
    if request.method == 'GET' and request.headers.get('Authorization'):
                
        tokenType, token = request.headers.get('Authorization').split()
        userId = request.headers.get('userId')

        if tokenType != 'Bearer': return 'Wrong token type.'
        if not token or token != os.environ.get('SECRET_TOKEN'): return 'Invalid Token.'
        if not userId: return 'Invalid User.'
        
        userChatInfo = db.user_chat_info
        userChatInfoDocument = userChatInfo.find_one({'_id': userId}) 

        if userChatInfoDocument:
            userChatInfoArray = refreshedChatInfo(userChatInfoDocument['chatInfo'])
            return jsonify({
                'error': False,
                'message': userChatInfoArray
            })
        else:
            return jsonify({
            'error': False,
            'message': [],
        })
    else:
        return jsonify({
            'error': True,
            'message': 'Access Denied.',
        })
        
@app.route('/v1/socket/messages')
@limiter.exempt
def fetchMesseges():
    if request.method == 'GET' and request.headers.get('Authorization'):

        if not request.headers.get('room'):
            return jsonify({
                'error': True,
                'message': 'Invalid room.'
            }) 

        room = request.headers.get('room')

        tokenType, token = request.headers.get('Authorization').split()
        if tokenType != 'Bearer':
            return jsonify({
                'error': True,
                'message': 'Invalid token type.'
            }) 
        if not token or token != os.environ.get('SECRET_TOKEN'):
            return jsonify({
                'error': True,
                'message': 'Invalid token.'
            }) 

        # Pointer to the user_messages collections
        userMessages = db.user_messages

        # Pointer to the array of messages of given room.
        chatMessagesDocument = userMessages.find_one({ '_id': room })
        if chatMessagesDocument:
            messagesOfGivenRoom = chatMessagesDocument['messages']
        else:
            messagesOfGivenRoom = []
        
        return jsonify({
            'error': False,
            'message': messagesOfGivenRoom,
        })
    else:
        return jsonify({
            'error': True,
            'message': 'Access Denied.'
        }) 


@app.route('/v1/socket/rooms', methods=['GET', 'POST'])
@limiter.exempt
def fetchRooms():
    if request.method == 'POST' and request.headers.get('Authorization'):

        room = request.headers.get('room')
        tokenType, token = request.headers.get('Authorization').split()
        if tokenType != 'Bearer':
            return jsonify({
                'error': True,
                'message': 'Invalid token type.'
            }) 
        if not token or token != os.environ.get('SECRET_TOKEN'):
            return jsonify({
                'error': True,
                'message': 'Invalid token'
            })
        
        addRoomIfNotPresent(room)
        return fetchRoomsFromDatabase()

    elif request.method == 'GET' and request.headers.get('Authorization'):
        return fetchRoomsFromDatabase()

    else:
        return jsonify({
            'error': True,
            'message': 'Access Denied.'
        }) 
  

# SOCKETS
@socket.on('connect')
def on_connect():
    pass


@socket.on('send_message')
def on_chat_sent(data):
    room = data['room']
    
    # Update the rooms
    addRoomIfNotPresent(room)

    # Update the messages
    addMessage(data)

    # Update the chatInfo
    addChatInfo(data)

    emit('private_message_sent', broadcast=True)

