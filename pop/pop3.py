from socket import socket
from typing import NoReturn
import ssl


class Pop3:
    def __init__(self):
        self.s = None

    def receive(self) -> str:
        data = b""
        part = b""
        try:
            while True:
                part = self.s.recv(1024)
                if not len(part):
                    break
                data += part
                part = b""
        except:
            data += part
        return data.decode()

    def send(self, command: str) -> NoReturn:
        self.s.sendall(f"{command}\r\n".encode())

    def connect(self, host: str, port: int) -> NoReturn:
        self.s = socket()
        self.s.settimeout(1)
        self.s = ssl.wrap_socket(self.s, ssl_version=ssl.PROTOCOL_SSLv23)
        self.s.connect((host, port))
        print(self.receive())

    def auth(self, username: str, password: str) -> bool:
        self.send(f"USER {username}")
        self.send(f"PASS {password}")
        answer = self.receive()
        print(answer)
        if answer.startswith('-ERR [AUTH]'):
            return False
        return True

    def get_headers(self, number: int = 1) -> NoReturn:
        self.send(f"TOP {number} 0")
        return self.receive()

    def get_letter(self, number: int = 1) -> NoReturn:
        self.send(f"RETR {number}")
        print(self.receive())
