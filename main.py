import argparse
import game
import server

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
    parser_client.set_defaults(C=True, S=False, ip='127.0.0.1')

    # parser for server functionality
    parser_server = subparsers.add_parser('server')
    parser_server.add_argument(
        "-S", help="Use to run pyMultiPoing as a server",
        action='store_const',
        const=True)
    parser_server.set_defaults(S=True, C=False, ip='127.0.0.1')

    args = parser.parse_args()

    if args.C:
        gameInstance = game.Game(args)
        gameInstance.start()
    if args.S:
        serverInstance = server.Server(args)
        serverInstance.start()
