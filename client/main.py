from argparse import ArgumentParser, Namespace
from typing import NoReturn
from getpass import getpass
import re
from pop.pop3 import Pop3


BOUNDARY = re.compile('Content-Type: multipart/mixed;\s+boundary="(.*?)"')


def parse_args() -> Namespace:
    parser = ArgumentParser()

    credentials = parser.add_argument_group('Credentials')
    credentials.add_argument('--host', type=str, required=True)
    credentials.add_argument('-p', '--port', type=int, required=True)
    credentials.add_argument('-u', '--username', type=str, required=True)
    credentials.add_argument('--password', type=str, default=None)

    action = parser.add_argument_group('Actions')
    action.add_argument('--headers', action='store_true',
                        help='Get last message headers')
    action.add_argument('--top', action='store_true',
                        help='Get a few first lines of the letter')
    action.add_argument('--full', action='store_true',
                        help='Get the full letter with attachments')

    args = parser.parse_args()
    if args.password is None:
        args.password = getpass()

    return args


def run() -> NoReturn:
    args = parse_args()
    pop = Pop3()
    pop.connect(args.host, args.port)
    if not pop.auth(args.username, args.password):
        print('Incorrect password')
        return
    pop.get_headers(1)


def parse_headers(headers: str) -> str:
    pass


if __name__ == '__main__':
    run()
