import curses
import command as cmd
from twisted.internet import reactor
from twisted.internet.protocol import Protocol, ClientFactory
from twisted.internet.task import LoopingCall

from twisted.python import log


from json import JSONDecoder, JSONEncoder
import logging

PORT = 8888
logging.basicConfig(filename='pyMultiPong.log',
                    level=logging.DEBUG, format='%(asctime)s %(message)s')


class Game:

    def __init__(self, args):
        self.startArgs = args

        logging.info('CLIENT: started client game instance')

        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        begin_x = 20
        begin_y = 7
        height = 5
        width = 40
        self.win = curses.newwin(height, width, begin_y, begin_x)
        self.win.clear()
        self.win.border()
        self.win.refresh()

        self.clientBuffer = cmd.commandBuffer()  # holds clientside commands
        self.clientState = "INIT"
        self.serverState = None
        self.playerNum = None

        self.paddleLeft = cmd.Paddle('left', 0, 5)
        self.paddleRight = cmd.Paddle('right', 0, 5)

        # intialize the client and network handlers
        self.clientInputHandler = cmd.InputHandler()

        # the network handler has to know which pipe to add commands to
        # since it processes commands outside of the game loop
        self.networkHandler = cmd.NetworkCommandHandler(self.clientBuffer)

        reactor.connectTCP(self.startArgs.ip, PORT,
                           ClientFactory(self.networkHandler))

        self.clientActor = None  # This gets set to the paddle we control
        self.serverActor = None  # This gets set to the paddle sever controls

    def periodic_task_crashed(reason):
        logging.info(reason.getErrorMessage() + "periodic_task broken")

    def start(self):
        lc = LoopingCall(self.loop())
        self.d = lc.start(1)
        self.d.addErrback(self.periodic_task_crashed)
        reactor.run()


    def loop(self):
        # run any commands we may have recieved over the network
        try:
            self.clientBuffer.runRemove()
            logging.info('loop')
            ch = self.win.getch()
            if(ch == curses.ERR):
                self.win.refresh()
            else:
                command = self.clientInputHandler.handleInput(ch)
                if command is not None:
                    self.clientBuffer.add(command)
        except:
            self.d.errback()


class Client(Protocol):

    def __init__(self, handler):
        self.handler = handler
        logging.info('CLIENT: started client protocol')

    def sendMessage(self, msg):
        self.transport.write(msg)

    def dataReceived(self, data):
        self.handler.handleNetwork(data)


class ClientFactory(ClientFactory):
    def __init__(self, handler):
        self.handler = handler
        logging.info('CLIENT: started client connection factory')

    def startedConnecting(self, connector):
        logging.info('CLIENT: Started to connect.')

    def buildProtocol(self, addr):
        logging.info('CLIENT: Connected.')
        return Client(self.handler)

    def clientConnectionLost(self, connector, reason):
        logging.info('CLIENT: Lost connection.  Reason:' + reason.getErrorMessage())

    def clientConnectionFailed(self, connector, reason):
        logging.info('CLIENT: Connection failed. Reason:' + reason.getErrorMessage())
