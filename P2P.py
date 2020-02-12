import random
from datetime import datetime
import os
import socket
import time
from threading import Thread
from tinydb import TinyDB

# Initiate a local tinyDB database
db = TinyDB('chats.json')

# Setup chats backup table in DB
chats_backup_table = db.table('chats')


class P2P:
    # Function to recieve messages sent by other users(devices) in the network
    def recieve_message(self):
        while True:
            message = self.broadcast_socket.recv(4096)  # Receive 4KB
            message_str = str(message.decode('utf-8'))  # Decode message to string
            if message_str.find(':') != -1:  # Find the username and message separator, to validate message format
                print(message_str)
                self.messages.append(message_str)  # Append to saved messages
            # Check if the message is not a 'quit', remove the user if it is quit message
            elif message_str.find('###') != -1 and message_str.find(':') == -1 and message_str[3:] in self.online_users:
                self.online_users.remove(message_str[3:])  # Remove user
                print('>> Current online users: ' + str(len(self.online_users)))
            # Check if user is new and not in list of alive hosts, add it to the list
            elif not (message_str in self.online_users) and message_str.find(':') == -1:
                self.online_users.append(message_str)
                print('>> Current online users: ' + str(len(self.online_users)))

    # Broadcast message to be sent to all other users(devices) in the network
    def broadcast_message(self):
        self.send_socket.setblocking(False)  # Set port as non blocking, to allow other threads to use it
        while True:
            data = input()  # Input message to be sent
            if data == '\q':  # If message is quit message
                close_message = '###' + self.name
                self.send_socket.sendto(close_message.encode('utf-8'),
                                        ('255.255.255.255', 8000))  # Send quitting broadcast message to other nodes
                chats_backup_table.insert(
                    {'name': self.name, 'messages': self.messages})  # Save the chat history till now
                os._exit(1)
            elif data != '':
                # Create the message to be sent in format of [<DATE>] <username> : message
                send_message = '[' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '] ' + self.name + ': ' + data
                self.send_socket.sendto(send_message.encode('utf-8'), ('255.255.255.255', 8000))

    # Broadcast to other users that you  are currently alive(online)
    def broadcast_online(self):
        self.send_socket.setblocking(False)  # Set port as non blocking, to allow other threads to use it
        while True:
            time.sleep(1)  # Send broadcast alive afer every 1 second
            self.send_socket.sendto(self.name.encode('utf-8'), ('255.255.255.255', 8000))  # Broadcast username

    def __init__(self):
        self.broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Use UDP
        self.broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Set socket to be reusable
        self.broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # Set socket to broadcasting mode
        self.broadcast_socket.bind(('0.0.0.0', 8000))

        self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Use UDP
        self.send_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # Set socket to be reusable

        self.receiving_thread = Thread(target=self.recieve_message)  # Create separate thread for receiving function
        self.send_thread = Thread(target=self.broadcast_message)  # Create separate thread for sending function

        self.online_users = []  # Maintain list of online users

        self.broadcast_online_status_thread = Thread(
            target=self.broadcast_online)  # Create separate thread for alive broadcasting function

        self.name = ''  # Username

        self.messages = []  # List of messages received till now

    def main(self):
        print('## P2P chat ##')
        print('->To broadcast message to all users, just enter your message')

        while self.name == '':  # Input username, should not be empty
            self.name = input('Enter your username: ')

        # Fetch previous chat history from database and print it
        try:
            print("-------Previous Message History--------")
            for message in chats_backup_table.all()[-1].get('messages'):
                print(message)
            print("---------------------------------------")
        except:
            print("-----------No Message History----------")
            pass

        # Start the 3 threads
        self.receiving_thread.start()
        self.send_thread.start()
        self.broadcast_online_status_thread.start()

        # Join the 3 threads on closure
        self.receiving_thread.join()
        self.send_thread.join()
        self.broadcast_online_status_thread.join()
