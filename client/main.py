from argparse import ArgumentParser, Namespace
from typing import NoReturn
from email.header import decode_header
from getpass import getpass
import re
import base64
from pop.pop3 import Pop3
from binascii import Error


BOUNDARY = re.compile(r'Content-Type: multipart/mixed;\s+boundary="(.*?)"',
                      flags=re.DOTALL | re.MULTILINE)
DATE = re.compile(r'Date: (.+)?[\r\n]+')
SUBJECT = re.compile(r'Subject: (((=\?.+?\?=)\s*)+)',
                     flags=re.MULTILINE)
FROM = re.compile(r'From: ((=\?.+?\?=)\s*)+<(.+?)>', flags=re.MULTILINE)
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
    if args.headers:
        headers = pop.get_headers(1)
        parse_headers(headers)
    if args.top:
        letter = pop.get_headers(1, 8)
        first_lines(letter)
    if args.full:
        letter = pop.get_letter(1)
        save_email(letter)


def parse_headers(headers: str) -> NoReturn:
    date = re.search(DATE, headers).group(1)

    subject = re.search(SUBJECT, headers).group(1)
    decoded_subject = ''
    for i in re.split(r'\s', subject):
        try:
            decoded_subject += decode_header(i)[0][0].decode()
        except AttributeError:
            pass

    to = re.search(TO, headers).group(1)

    print(f'Date: {date}')
    print(f'Subject: {decoded_subject}')
    print(f'To: {to}')


def first_lines(content: str) -> NoReturn:
    match = re.search(BOUNDARY, content)
    boundary = match.group(1)

    parts = re.split(f'--{boundary}', content)

    text = parts[1]
    text_lines = re.split('\r\n\r\n', text)
    text_headers, text_content = text_lines[0], text_lines[1]
    try:
        print(base64.b64decode(text_content.strip('.\n\t\r')).decode())
    except Error:
        print(text_content.strip('.\n\t\r'))


def save_email(content: str) -> NoReturn:
    match = re.search(BOUNDARY, content)
    boundary = match.group(1)

    parts = re.split(f'--{boundary}', content)

    text = parts[1]
    text_lines = re.split('\r\n\r\n', text)
    text_headers, text_content = text_lines[0], text_lines[1]
    with open('text.txt', 'w') as f:
        f.write(text_content)

    attachments = parts[2:]
    for attachment in attachments:
        try:
            attachment_lines = re.split('\r\n\r\n', attachment)
            attachment_headers, attachment_content = (attachment_lines[0],
                                                      attachment_lines[1])
            file_name = re.search('name="(.+?)"', attachment_headers).group(1)
            with open(file_name, 'wb') as f:
                f.write(base64.b64decode(attachment_content))
        except IndexError:
            pass


if __name__ == '__main__':
    run()
