import sys

from autobahn.websocket import WebSocketServerProtocol, WebSocketServerFactory, listenWS
from twisted.internet import reactor

class ClientConnection(WebSocketServerProtocol):
	def onOpen(self):
		self.factory.register(self)

	def onMessage(self, message, binary):
		if binary:
			return
		self.factory.processMessage(self, message)

	def connectionLost(self, reason):
		WebSocketServerProtocol.connectionLost(self, reason)
		self.factory.unregister(self)

class Server(WebSocketServerFactory):
	def __init__(self, url, debug = False, debugCodePaths = False):
		WebSocketServerFactory.__init__(self, url, debug = debug, debugCodePaths = debugCodePaths)
		self.clients = []

	def processMessage(self, client, message):
		print "Received message from {client}: {message}".format(client=client.peerstr, message=message)

	def register(self, client):
		if not client in self.clients:
			self.clients.append(client)
			print "Client {client} connected".format(client=client.peerstr)

	def unregister(self, client):
		if client in self.clients:
			self.clients.remove(client)
			print "Client {client} disconnected".format(client=client.peerstr)

	def sendMessageSingle(self, client, message):
		client.sendMessage(message)

	def sendMessageMultiple(self, clients, message):
		preparedMessage = self.prepareMessage(message)
		for client in clients:
			client.sendMessage(preparedMessage)

def main():
	if len(sys.argv) > 2:
		host = sys.argv[1]
		port = sys.argv[2]
	else:
		host = "127.0.0.1"
		port = sys.argv[1]

	print "Starting server on {host}:{port}".format(host=host, port=port)
	factory = Server("ws://{host}:{port}".format(host=host, port=port))
	factory.protocol = ClientConnection
	factory.setProtocolOptions(allowHixie76=True)
	# listenWS(factory, interface=host)
	listenWS(factory)
	reactor.run()


if __name__ == '__main__':
	main()