import socket
import ssl
import base64
import re

from typing import NoReturn


host_addr = 'pop.yandex.ru'
port = 995
user_name = 'USERNAME'
password = 'PASSWORD'


EMAIL_PTTRN = re.compile('Content-Type: multipart/mixed;\s+boundary="(.*?)"')


def send(s: socket.socket, command: str) -> NoReturn:
    s.sendall("{}\r\n".format(command).encode())


def receive(s: socket.socket) -> str:
    data = b""

    part = b""
    try:
        while True:
            part = s.recv(1024)
            if not len(part):
                break
            data += part
            part = b""
    except:
        data += part

    return data.decode()


sock = socket.socket()
sock.settimeout(1)
sock = ssl.wrap_socket(sock, ssl_version=ssl.PROTOCOL_SSLv23)
sock.connect((host_addr, port))
print(sock.recv(1024).decode())

send(sock, "USER {}".format(user_name))
send(sock, "PASS {}".format(password))
print(receive(sock))

send(sock, "STAT")
print(receive(sock))

send(sock, "LIST")
print(receive(sock))

send(sock, "RETR {}".format(2))
mail = receive(sock)

match = re.search(EMAIL_PTTRN, mail)
boundary = match.group(1)

parts = re.split('--{}'.format(boundary), mail)

text = parts[1]
text_lines = re.split('\r\n\r\n', text)
text_headers, text_content = text_lines[0], text_lines[1]
with open('text.txt', 'w') as f:
    f.write(text_content)

attachment = parts[2]
attachment_lines = re.split('\r\n\r\n', attachment)
attachment_headers, attachment_content = (attachment_lines[0],
                                          attachment_lines[1])
file_name = re.search('name="(.+?)"', attachment_headers).group(1)
with open(file_name, 'wb') as f:
    f.write(base64.b64decode(attachment_content))
