import os
from flask import jsonify, request
from flask_socketio import emit, join_room
from .. import app, socket, db


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
    # Pointer to user messages collection
    userMessages = db.user_messages

    # Updation of the userMessages array.
    userMessages.find_one_and_update({'_id': 'chatMessages'}, {'$push': {'chatMessages': data}})


@app.route('/socket/chats')
def fetchChats():
    if request.method == 'GET' and request.headers.get('Authorization'):
        
        if not request.headers.get('userId'): return 'No user sent.'
        
        tokenType, token = request.headers.get('Authorization').split()
        userId = request.headers.get('userId')

        if tokenType != 'Bearer': return 'Wrong token type.'
        if not token or token != os.environ.get('SECRET_TOKEN'): return 'Invalid Token.'
        if not userId: return 'Invalid User.'
        

        userChatInfo = db.user_chat_info
        userChatInfoDocument = userChatInfo.find_one({'_id': userId}) 
        if userChatInfoDocument:
            userChatInfoArray = userChatInfoDocument['chatInfo']
            return jsonify({
                'error': False,
                'message': userChatInfoArray
            })
        else:
            return jsonify({
            'error': True,
            'message': 'No chat information available.'
        })
    else:
        return jsonify({
            'error': True,
            'message': 'Access Denied.'
        })
        

@app.route('/socket/messages')
def fetchMesseges():
    if request.method == 'GET' and request.headers.get('Authorization'):

        if not request.headers.get('room'): return 'Room Required.'
        room = request.headers.get('room')

        tokenType, token = request.headers.get('Authorization').split()
        if tokenType != 'Bearer': return 'Wrong token type.'
        if not token or token != os.environ.get('SECRET_TOKEN'): return 'Invalid Token.'


        # Pointer to the user_messages collections
        userMessages = db.user_messages

        # Pointer to the array of chatMessages.
        chatMessagesDocument = userMessages.find_one({'_id': 'chatMessages'})
        chatMessages = chatMessagesDocument['chatMessages']
        
        messagesOfGivenRoom = [message for message in chatMessages if message['room'] == room]


        return jsonify({
            'error': False,
            'message': messagesOfGivenRoom,
        })
    else:
        return jsonify({
            'error': True,
            'message': 'Access Denied.'
        }) 


@app.route('/socket/rooms', methods=['GET', 'POST'])
def fetchRooms():
    if request.method == 'POST' and request.headers.get('Authorization'):

        room = request.headers.get('room')
        tokenType, token = request.headers.get('Authorization').split()
        if tokenType != 'Bearer': return 'Wrong token type.'
        if not token or token != os.environ.get('SECRET_TOKEN'): return 'Invalid Token.'
        
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


@socket.on('join_room')
def on_join(data):
    room = data['room']
    addRoomIfNotPresent(room)
 
    join_room(room)
    emit('open_room', {'room': room}, broadcast=True)


@socket.on('send_message')
def on_chat_sent(data):
    room = data['room']
    addRoomIfNotPresent(room)

    addMessage(data)
    
    emit('message_sent', {'data': data }, broadcast=True)
    emit('private_message_sent', broadcast=True)

