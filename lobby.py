from uuid import uuid4

from player import Player
from message import Message
from game import Game
from apple import Apple

class Lobby(object):
	def __init__(self, server):
		self.server = server
		self.players = {}
		self.games = {}
		self.message_handlers = {
				Message.RECEIVE_SESSION_ID_EXISTING: self.receiveSessionId,
				Message.RECEIVE_CREATE_GAME_REQUEST: self.createGame,
				Message.RECEIVE_SESSION_ID_REQUEST: self.requestSessionId,
				Message.RECEIVE_PLAYER_JOIN_GAME: self.joinGame,
				Message.RECEIVE_GAME_START: self.startRound,
				Message.RECEIVE_PLAYER_USE_RED_APPLE: self.useRedApple,
				Message.RECEIVE_PLAYER_SELECT_WINNER: self.selectWinningRedApple
		}
		self.red_apples = [
				Apple(Apple.TYPE_RED, "Bob Marley"),
				Apple(Apple.TYPE_RED, "The Wild West"),
				Apple(Apple.TYPE_RED, "Mariska Hargitay"),
				Apple(Apple.TYPE_RED, "Walk on the Beach"),
				Apple(Apple.TYPE_RED, "Incestuous Affair"),
				Apple(Apple.TYPE_RED, "Flaming Homosexual")
		]
		self.green_apples = [
				Apple(Apple.TYPE_GREEN, "Fabulous"),
				Apple(Apple.TYPE_GREEN, "Deviant")
		]

	def playerJoinLobby(self, connection):
		pass

	def playerLeaveLobby(self, connection):
		pass

	def processMessage(self, connection, encodedMessage):
		message = Message.decode(encodedMessage)
		self.message_handlers[message['type']](connection, message['payload'])

	def requestSessionId(self, connection, player_name):
		session_id = uuid4().hex
		player = Player(connection)
		player.session_id = session_id
		player.name = player_name
		self.players[session_id] = player

		message = Message.encode(Message.SEND_SESSION_ID, session_id)
		self.server.sendMessageSingle(player.connection, message)

	def receiveSessionId(self, connection, session_id):
		if session_id in self.players:
			player = self.players[session_id]
			player.connection = connection
			connection.player = player

	def createGame(self, connection, game_name):
		if game_name not in self.games:
			game = Game(game_name, self.red_apples, self.green_apples)
			self.games[game_name] = game
			game.players.append(connection.player)
			connection.player.game = game
			game.master = connection.player
			message = Message.encode(Message.SEND_CREATE_GAME_SUCCESS, game_name)
		else:
			message = Message.encode(Message.SEND_CREATE_GAME_FAILURE, '')
		self.server.sendMessageSingle(connection, message)

	def joinGame(self, connection, game_name):
		if game_name in self.games:
			game = self.games[game_name]
			if not game.in_progress:
				game.players.append(connection.player)
				connection.player.game = game
				message = Message.encode(Message.SEND_PLAYER_JOIN_GAME_SUCCESS, game_name)
			else:
				message = Message.encode(Message.SEND_PLAYER_JOIN_GAME_FAILURE, "Game is in progress...")	
		else:
			message = Message.encode(Message.SEND_PLAYER_JOIN_GAME_FAILURE, "Game does not exist...")
		self.server.sendMessageSingle(connection, message)

	def startRound(self, connection):
		game = connection.player.game
		if game.state != Game.STATE_FINISHED_ROUND:
			return
		# if game.master is connection.player:
		# game.start()
		game.startNewRound()

		# message = Message.encode(Message.SEND_GAME_MESSAGE_STARTED, '')
		# self.server.sendMessageMultiple(game.players, message)

		scores = {}
		connections = []
		for player in game.players:
			connections.append(player.connection)
			scores[player.name] = len(player.green_apples)
			red_apples = []
			for red_apple in player.red_apples:
				red_apples.append(red_apple.dictionary)
			message = Message.encode(Message.SEND_GAME_MESSAGE_PLAYER_RED_APPLES, red_apples)
			self.server.sendMessageSingle(player.connection, message)

		round_details = {}
		round_details['JUDGE'] = game.players[game.judge]
		round_details['SCORES'] = scores
		message = Message.encode(Message.SEND_GAME_MESSAGE_ROUND_DETAILS, round_details)
		self.server.sendMessageMultiple(connections, message)

	def useRedApple(self, connection, card_id):
		player = connection.player
		game = player.game
		card_id = int(card_id)

		if game.state == Game.STATE_WAITING_FOR_RED_APPLES:
			if player is not game.players[game.judge]:
				if card_id >= 0 and card_id < len(player.red_apples):
					if player.active_red_apple is None:
						player.active_red_apple = card_id

		if game.isReadyToJudge() == Game.STATE_JUDGING:
			cards = {}
			judge = game.players[game.judge]
			for player in game.players:
				if player is judge:
					continue
				cards[game.players.index(player)] = player.red_apples.pop(player.active_red_apple).dictionary
			message = Message.encode(Message.SEND_GAME_MESSAGE_ROUND_RED_APPLES, cards)
			self.server.sendMessageSingle(judge.connection, message)

	def selectWinningRedApple(self, connection, player_id):
		judge = connection.player
		game = judge.game
		winner = game.players[player_id]

		if game.state == Game.STATE_JUDGING:
			if judge is game.players[game.judge]:
				if winner is not judge:
					winner.green_apples.append(game.active_green_apple)
					game.active_green_apple = None
					game.state = Game.STATE_FINISHED_ROUND
					self.startRound(connection)