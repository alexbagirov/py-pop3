from argparse import ArgumentParser, Namespace
from typing import NoReturn
from email.header import decode_header
from getpass import getpass
import re
from pop.pop3 import Pop3


BOUNDARY = re.compile(r'Content-Type: multipart/mixed;\s+boundary="(.*?)"',
                      flags=re.DOTALL | re.MULTILINE)
DATE = re.compile(r'Date: (.+)?[\r\n]+')
SUBJECT = re.compile(r'Subject: ((=\?.+?\?=)\s*)+',
                     flags=re.MULTILINE)
FROM = re.compile(r'From: ((=\?.+?\?=)\s*)+<(.+?)>',
                  flags=re.DOTALL | re.MULTILINE)
TO = re.compile(r'To: (.+)?[\r\n]+')


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
    headers = pop.get_headers(1)
    print(headers)
    parse_headers(headers)


def parse_headers(headers: str) -> NoReturn:
    date = re.search(DATE, headers).group(1)
    subject = re.findall(SUBJECT, headers)
    decoded_subject = ''
    for i in subject:
        decoded_subject += decode_header(i)[0][0].decode()
    # subject = sum(map(decode_header, subject))
    from_data = re.findall(FROM, headers)
    from_name, from_email = from_data[:-1], from_data[-1]
    from_name = sum(map(decode_header, from_name))
    to = re.search(TO, headers).group(1)

    print(date)
    print(subject)
    print(from_name)
    print(from_email)
    print(to)


if __name__ == '__main__':
    run()
