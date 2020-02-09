import random
from datetime import datetime
import os
import socket
import time
from threading import Thread
from tinydb import TinyDB

db = TinyDB('chats.json')

chats_backup_table = db.table('chats')


class P2P:
    def recieve_message(self):
        while True:
            message = self.broadcast_socket.recv(4096)
            message_str = str(message.decode('utf-8'))
            if message_str.find(':') != -1:
                print(message_str)
                self.messages.append(message_str)
            elif message_str.find('###') != -1 and message_str.find(':') == -1 and message_str[3:] in self.online_users:
                self.online_users.remove(message_str[3:])
                print('>> Current online users: ' + str(len(self.online_users)))
            elif not (message_str in self.online_users) and message_str.find(':') == -1:
                self.online_users.append(message_str)
                print('>> Current online users: ' + str(len(self.online_users)))

    def generate_unique_username(self):
        self.name = "%06x" % random.randint(0, 0xFFFFFF)
        pass

    def send_specific_user(self):
        pass

    def cleanup(self):
        # alive = [0] * len(self.on)
        # remove hosts from which no ping!
        pass

    def broadcast_message(self):
        self.send_socket.setblocking(False)
        while True:
            data = input()
            if data == '\q':
                close_message = '###' + self.name
                self.send_socket.sendto(close_message.encode('utf-8'), ('255.255.255.255', 8000))
                chats_backup_table.insert({'name': self.name, 'messages': self.messages})
                os._exit(1)
            elif data != '':
                send_message = '[' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '] ' + self.name + ': ' + data
                self.send_socket.sendto(send_message.encode('utf-8'), ('255.255.255.255', 8000))

    def broadcast_online(self):
        self.send_socket.setblocking(False)
        while True:
            time.sleep(1)
            self.send_socket.sendto(self.name.encode('utf-8'), ('255.255.255.255', 8000))

    def __init__(self):
        self.broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.broadcast_socket.bind(('0.0.0.0', 8000))

        self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.send_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        self.receiving_thread = Thread(target=self.recieve_message)
        self.send_thread = Thread(target=self.broadcast_message)

        self.online_users = []

        self.broadcast_online_status_thread = Thread(target=self.broadcast_online)

        self.name = ''

        self.messages = []

    def main(self):
        print('## P2P chat ##')
        print('->To broadcast message to all users, just enter your message')

        while self.name == '':
            self.name = input('Enter your username: ')

        try:
            print("-------Previous Message History--------")
            for message in chats_backup_table.all()[-1].get('messages'):
                print(message)
            print("---------------------------------------")
        except:
            print("-----------No Message History----------")
            pass

        self.receiving_thread.start()
        self.send_thread.start()
        self.broadcast_online_status_thread.start()

        self.receiving_thread.join()
        self.send_thread.join()
        self.broadcast_online_status_thread.join()


if __name__ == '__main__':
    p2p = P2P()
    p2p.main()
