class Player(object):
	def __init__(self, connection):
		self.name = ''
		self.session_id = None
		self.red_apples = []
		self.green_apples = []
		self.game = None
		self.connection = connection
		self.connection.player = self
		self.active_red_apple = None
		self.inactive_since = None