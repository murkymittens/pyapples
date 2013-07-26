import json

class Message(object):
	SYSTEM_MESSAGE = 0
	GIVE_SESSION_ID = 1

	@staticmethod
	def encode(type, payload):
		return json.dumps({'type': type, 'payload': payload})

	@staticmethod
	def decode(message):
		return json.loads(message)