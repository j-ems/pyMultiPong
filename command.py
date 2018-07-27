from json import JSONDecoder, JSONEncoder
import logging
import curses

logging.basicConfig(filename='pyMultiPong.log',
                    level=logging.DEBUG, format='%(asctime)s %(message)s')

class Paddle:
    def __init__(self, side, color, length):
        self.side = side
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


class commandBuffer:  # An object that holds commands and executes them
    def __init__(self):
        self.commands = []

    def add(self, command):
        self.commands.append(command)

    def runRemove(self):  # run commands and then delete after execution
        for c in self.commands:
            c.execute()
            self.commands.remove(c)

    def runStore(self, buffer):  # run commands and then store them in buffer
        for c in self.commands:
            c.execute()
            buffer.add(c)

    def undoRemove(self):
        for c in self.commands:
            c.undo()
            self.commands.remove(c)


class Command:
    isvalid = False

    def execute(self):
        pass

    def undo(self):
        pass


class upCommand(Command):
    def __init__(self, actor):
        self.actor = actor
        self.isvalid = True
        logging.debug('Up')

    def execute(self):
        self.actor.up()

    def undo(self):
        self.actor.down()


class downCommand(Command):
    def __init__(self, actor):
        self.actor = actor
        self.isvalid = True
        logging.debug('Down')

    def execute(self):
        self.actor.down()

    def undo(self):
        self.actor.up()


class scoreCommand(Command):
    def __init__(self, game, scores):
        self.game = game
        self.isvalid = True
        self.scores = scores

    def execute(self):
        self.oldscores = self.game.getScores()
        self.game.setScores(self.scores)

    def undo(self):
        self.game.setScores(self.oldscores)


class InputHandler():
    def handleInput(ch, actor):
        if ch == curses.KEY_UP:
            return upCommand(actor)
        if ch == curses.KEY_DOWN:
            return downCommand(actor)


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
