from random import shuffle

class Game(object):
	def __init__(self, name, red_apples, green_apples):
		self.name = name
		self.players = []
		self.red_apples = red_apples[:]
		self.green_apples = green_apples[:]
		self.judge = 0

		shuffle(self.red_apples)
		shuffle(self.green_apples)