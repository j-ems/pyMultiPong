import argparse
import curses
from multiprocessing import Process
from server import Server

from twisted.internet import reactor
from twisted.internet.protocol import Protocol, ClientFactory
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol

from json import JSONDecoder, JSONEncoder
import logging

PORT = 8888
logging.basicConfig(filename='pyMultiPong_client.log',
                    level=logging.DEBUG, format='%(asctime)s %(message)s')


class Game:

    def __init__(self, args):
        self.startArgs = args

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

        self.gamePipe = Pipeline()  # this holds our clientside commands
        self.clientState = "INIT"
        self.serverState = None

        reactor.connectTCP(self.startArgs.ip, PORT, ClientFactory())
        reactor.run()

    def loop(self):
        ch = curses.getch()
        if(ch == curses.ERR):
            curses.refresh()
        else:
            command = InputHandler.handleInput(ch)
            self.gamePipe.add(command)


class Paddle:
    def __init__(self, posX, posY, color, length):
        self.posX = posX
        self.posY = posY
        self.color = color
        self.length = length

    def draw(self, window):
        for i in range(self.length):
            window.addch(self.posY + i,
                         self.posX, ' ',
                         curses.color_pair(self.color))

    def up(self):
        self.posY = self.posY + 1

    def down(self):
        self.posY = self.posY - 1


class Pipeline:  # An object that holds commands and executes them
    def __init__(self):
        self.commands = []

    def add(self, command):
        self.commands.append(command)

    def run(self):
        for c in self.commands:
            c.execute()


class Command:
    def execute(self, actor):
        pass


class upCommand(Command):
    def execute(self, actor):
        actor.up()


class downCommand(Command):
    def execute(self, actor):
        actor.down()


class InputHandler():
    def handleInput(ch):
        if ch == curses.KEY_UP:
            return upCommand()
        if ch == curses.KEY_DOWN:
            return downCommand()


class NetworkCommandHandler():
    def __init__(self, pipe):
        self.pipe = pipe

    def handleNetwork(self, data):
        try:
            response = JSONDecoder().decode(data)
            response.serverState
            # todo: add the command handling
        except ValueError:
            logging.warning("incoming data was malformated")


class Client(Protocol):

    def __init__(self, handler):
        self.handler = handler

    def sendMessage(self, msg):
        self.transport.write(msg)

    def dataReceived(self, data):
        self.handler.handleNetwork(data)


class ClientFactory(ClientFactory):
    def __init__(self, handler):
        self.handler = handler

    def startedConnecting(self, connector):
        logging.info('Started to connect.')

    def buildProtocol(self, addr):
        logging.info('Connected.')
        return Client(self.handler)

    def clientConnectionLost(self, connector, reason):
        logging.info('Lost connection.  Reason:', reason)

    def clientConnectionFailed(self, connector, reason):
        logging.info('Connection failed. Reason:', reason)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="pyMultiPong, a multiplayer curses pong game")
    subparsers = parser.add_subparsers()

    # parser for client functionality
    parser_client = subparsers.add_parser('client')
    parser_client.add_argument(
        "-C", help="Use to run pyMultiPoing as a client",
        action='store_const',
        const=True)
    parser_client.add_argument(
        "--ip", help="specify server to connect to", required=False)
    parser_client.set_defaults(C=True, ip='127.0.0.1')

    # parser for server functionality
    parser_server = subparsers.add_parser('server')
    parser_server.add_argument(
        "-S", help="Use to run pyMultiPoing as a server",
        action='store_const',
        const=True)
    parser_server.add_argument(
        "--nogame", help="Run pyMultiPong server without playing the game",
        action='store_const',
        const=True)
    parser_server.set_defaults(S=True, nogame=False, ip='127.0.0.1')

    args = parser.parse_args()

    if args.nogame is False:
        game = Game(args)
    if args.S:
        server = Server(args)
        serverProcess = Process(target=server)
        serverProcess.start()
