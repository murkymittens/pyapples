class Player(object):
	def __init__(self, name):
		self.name = name
		self.session_id = None
		self.red_apples = []
		self.green_apples = []