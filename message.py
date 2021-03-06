import json

class Message(object):
	SEND_SYSTEM_MESSAGE = 0
	SEND_SESSION_ID = 1
	RECEIVE_SESSION_ID_EXISTING = 2
	RECEIVE_CREATE_GAME_REQUEST = 3
	SEND_CREATE_GAME_SUCCESS = 4
	SEND_CREATE_GAME_FAILURE = 5
	RECEIVE_SESSION_ID_REQUEST = 6
	RECEIVE_PLAYER_JOIN_GAME = 7
	SEND_PLAYER_JOIN_GAME_SUCCESS = 8
	SEND_PLAYER_JOIN_GAME_FAILURE = 9
	SEND_GAME_MESSAGE_STARTED = 10
	SEND_GAME_MESSAGE_ROUND_DETAILS = 11
	SEND_GAME_MESSAGE_PLAYER_RED_APPLES = 12
	SEND_GAME_MESSAGE_ROUND_RED_APPLES = 13
	RECEIVE_GAME_START = 14
	RECEIVE_PLAYER_USE_RED_APPLE = 15
	RECEIVE_PLAYER_SELECT_WINNER = 16
	RECEIVE_CHAT_MESSAGE = 17
	SEND_CHAT_MESSAGE = 18
	SEND_PLAYER_JOINED_NOTIFICATION = 19

	@staticmethod
	def encode(type, payload):
		return json.dumps({'type': type, 'payload': payload})

	@staticmethod
	def decode(message):
		return json.loads(message)