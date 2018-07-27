from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from json import JSONDecoder, JSONEncoder
import logging
import command as cmd

PORT = 8888

logging.basicConfig(filename='pyMultiPong.log',
                    level=logging.DEBUG, format='%(asctime)s %(message)s')


class Server:
    def __init__(self, args):
        self.startArgs = args

    def start(self):
        logging.info('SERVER: started server process')

        self.factory = GameConnectionFactory()
        reactor.listenTCP(PORT, self.factory)
        self.state = GameState()

        gameLoopCaller = LoopingCall(self.gameLoop())
        gameLoopCaller.start(1, now=True)
        reactor.run()


    def stop(self):
        reactor.stop()
        logging.info("SERVER: Server stopped")

    def gameLoop(self):
        self.state.playersConnected = len(self.factory.users)
        print('test')




class GameState:

    playersConnected = 0

    gameStateHistory = []
    unprocessedUserInputs = cmd.commandBuffer()
    processedUserInputs = cmd.commandBuffer()

    currentGameState = gameStateHistory[-1:]

    def __init__(self):
        pass


class PongReciever(LineReceiver):

    def __init__(self, users):
        self.users = users
        self.name = None
        self.screenSizeX = None
        self.screenSizeY = None
        self.state = "INIT"
        logging.info('SERVER: started server PongReciever')

    def connectionMade(self):
        pass

    def connectionLost(self,reason):
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
            self.users[self.name] = self
            self.state = "GAME"
            logging.info("SERVER: Player " + self.users + " joined")

        except ValueError:
            logging.debug('SERVER: Malformated JSON init response')

    def handle_INCOMING(self, line):
        try:
            response = JSONDecoder().decode(line)
            for name, protocol in self.users.iteritems():
                if protocol != self:
                    protocol.sendLine(line)

        except ValueError:
            logging.debug('SERVER: Malformated JSON init response')


class GameConnectionFactory(Factory):

    def __init__(self):
        self.users = {}
        logging.info('SERVER: started server GameConnectionFactory')

    def buildProtocol(self, addr):
        return PongReciever(self.users)
