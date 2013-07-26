class Player(object):
	def __init__(self, connection):
		self.name = ''
		self.session_id = None
		self.red_apples = []
		self.green_apples = []
		self.game = None
		self.connection = connection