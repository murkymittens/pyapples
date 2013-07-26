import json

class Message(object):
	SYSTEM_MESSAGE = 0

	def encode(type, payload):
		return json.dumps({'type': type, 'payload': payload})

	def decode(message):
		return json.loads(message)