from uuid import uuid4

from player import Player
from message import Message

class Lobby(object):
	def __init__(self, server):
		self.server = server
		self.players = {}
		self.games = {}

	def playerJoinLobby(self, connection):
		session_id = uuid4().hex
		player = Player(connection)
		player.session_id = session_id
		self.players[session_id] = player

		message = Message.encode(Message.SYSTEM_MESSAGE, "Welcome to the Apples to Apples lobby!")
		self.server.sendMessageSingle(player.connection, message)

	def playerLeaveLobby(self, connection):
		pass

	def processMessage(self, connection, encodedMessage):
		message = Message.decode(encodedMessage)
		print message