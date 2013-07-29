import sqlite3
from uuid import uuid4
from time import time

from player import Player
from message import Message
from game import Game
from apple import Apple
from card_scraper import strip_tags

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
				Message.RECEIVE_PLAYER_SELECT_WINNER: self.selectWinningRedApple,
				Message.RECEIVE_CHAT_MESSAGE: self.receiveChatMessage
		}
		self.red_apples = []
		self.green_apples = []
		self.inactive_players = []

		sql = sqlite3.connect("apples.db")
		cur = sql.cursor()

		for row in cur.execute("SELECT * FROM green_apples"):
			self.green_apples.append(Apple(Apple.TYPE_GREEN, row[0], row[1]))
		
		for row in cur.execute("SELECT * FROM red_apples"):
			self.red_apples.append(Apple(Apple.TYPE_RED, row[0], row[1]))

		sql.close()

	def purge(self):
		self.purgeInactivePlayers()
		self.purgeInactiveGames()

	def purgeInactiveGames(self):
		games_to_purge = [x for x in self.games if not self.isGameActive(x)]
		for game in games_to_purge:
			print "Removing {game} for no players.".format(game=game.name)
			del self.games[game.name]

	def isGameActive(self, game):
		return len(self.games[game].players) > 0

	def purgeInactivePlayers(self):
		players_to_purge = [x for x in self.inactive_players if not self.isPlayerActive(x)]
		for player in players_to_purge:
			print "Removing {player} for inactivity.".format(player=player.name)
			del self.players[player.session_id]
			if player.game is not None:
				player.game.players.remove(player)
				player.game.startNewRound()

	def isPlayerActive(self, player):
		return time() - player.inactive_since < 300

	def playerJoinLobby(self, connection):
		pass

	def playerLeaveLobby(self, connection):
		self.inactive_players.append(connection.player)
		connection.player.inactive_since = time()
		connection.player.connection = None
		connection.player = None

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
				connections = []
				for player in game.players:
					connections.append(player.connection)
				message = Message.encode(Message.SEND_PLAYER_JOINED_NOTIFICATION, connection.player.name)
				self.server.sendMessageMultiple(connections, message)

				game.players.append(connection.player)
				connection.player.game = game
				message = Message.encode(Message.SEND_PLAYER_JOIN_GAME_SUCCESS, game_name)
			else:
				message = Message.encode(Message.SEND_PLAYER_JOIN_GAME_FAILURE, "Game is in progress...")	
		else:
			message = Message.encode(Message.SEND_PLAYER_JOIN_GAME_FAILURE, "Game does not exist...")
		self.server.sendMessageSingle(connection, message)

	def startRound(self, connection, *args):
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
		round_details['JUDGE'] = game.players[game.judge].name
		round_details['SCORES'] = scores
		round_details['GREEN_APPLE'] = game.active_green_apple.dictionary
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
		player_id = int(player_id)
		winner = game.players[player_id]

		if game.state == Game.STATE_JUDGING:
			if judge is game.players[game.judge]:
				if winner is not judge:
					winner.green_apples.append(game.active_green_apple)
					game.active_green_apple = None
					game.state = Game.STATE_FINISHED_ROUND
					self.startRound(connection)

	def receiveChatMessage(self, connection, message):
		connections = []
		chat_message = {}
		chat_message['name'] = connection.player.name
		chat_message['msg'] = strip_tags(message)
		game = connection.player.game
		for player in game.players:
			connections.append(player.connection)
		encmessage = Message.encode(Message.SEND_CHAT_MESSAGE, chat_message)
		self.server.sendMessageMultiple(connections, encmessage)