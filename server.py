from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor
from json import JSONDecoder, JSONEncoder
import logging

PORT = 8888

logging.basicConfig(filename='pyMultiPong_server.log',
                    level=logging.DEBUG, format='%(asctime)s %(message)s')


class Server:
    def run(self):
        reactor.listenTCP(PORT, GameConnectionFactory())
        reactor.run()

    def stop(self):
        reactor.stop()
        logging.info("Server stopped")


class PongReciever(LineReceiver):

    def __init__(self, users):
        self.users = users
        self.name = None
        self.screenSizeX = None
        self.screenSizeY = None
        self.state = "INIT"

    def connectionMade(self):
        pass

    def connectionLost(self):
        if self.name in self.users:
            del self.users[self.name]

    def lineRecieved(self, line):
        if self.state == "INIT":
            self.handle_INIT(line)
        else:
            self.handle_INCOMING()

    def handle_INIT(self, line):
        try:
            response = JSONDecoder().decode(line)
            self.name = len(self.users) + 1
            self.screenSize = response.screenSize
            self.users[self.name] = self
            self.state = "GAME"
            logging.info("Player " + self.users + " joined")

        except ValueError:
            logging.debug('Malformated JSON init response')

    def handle_INCOMING(self, line):
        try:
            response = JSONDecoder().decode(line)
            for name, protocol in self.users.iteritems():
                if protocol != self:
                    protocol.sendLine(line)

        except ValueError:
            logging.debug('Malformated JSON init response')


class GameConnectionFactory(Factory):

    def __init__(self):
        self.users = {}

    def buildProtocol(self, addr):
        return PongReciever(self.users)
