class Apple(object):
	TYPE_RED = 0
	TYPE_GREEN = 1

	def __init__(self, type, word, flavour = ''):
		self.type = type
		self.word = word
		self.flavour = flavour
		self.dictionary = {}
		self.dictionary['word'] = self.word
		self.dictionary['flavour'] = self.flavour
