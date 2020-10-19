#! /usr/bin/env python3

'''
Author: Jose Eduardo Soto

Description:
    This is the server module for file transfering program. To have
    good communication between the client and server there have to be little
    protocol strings that signify certain events. There must be an arbitruary byte
    length that must be enforced. Client will have to dictate it with the length of
    of the buffer it has to read.

    Only needs to handle 1 client.
'''

import os, socket, sys, threading

sys.path.append('../framed-echo')
from framedSock import framedReceive


listening_port, listening_addr = 50001, ''


DATA_SIZE = 80 # 79 + newline
TOKEN = '\0' #I don't know if this extends to other protocals or programs but
# it works for mine. When encoded it is not the same as b'' so its good.

filename = ''
state = 'f'
thread_number = 0

def main():
    #Servers need IBLA, which stands for initiate, bind, listen, and accept.
    s_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #ipv4 and tcp settings
    s_sock.bind((listening_addr, listening_port))
    s_sock.listen(1)

    while True:
        os.write(1, 'Listening for clients...'.encode())
        try:
            client_sock, client_addr = s_sock.accept()
            client_thread = TCPClientSession(client_sock, client_addr)
            os.write(1, 'captured client.\n'.encode())
        except KeyboardInterrupt:
            print('Closing server.')
            client_sock.close()
            break

    s_sock.close()

class TCPClientSession (threading.Thread):

        def __init__(self, client_socket, client_address):
            global thread_number
            thread_number += 1
            threading.Thread.__init__(self, name='ClientSession%d' % thread_number)
            self.lock = threading.Lock()
            self.c_sock = client_socket
            self.c_addr = client_address
            self.client_sock_fd = self.c_sock.fileno()
            self.client_ip, self.client_port = self.c_addr
            self.filename = ''
            self.file_fd = None
            self.state = 'f'


        #Inherited Thread method. Does receiving and writing logic here.
        def run(self):
            global DATA_SIZE
            self.lock.aquire()
            working = True
            while working:
                #print('[[Reading from socket]]')
                data = os.read(self.client_sock_fd, DATA_SIZE)
                if data is b'':
                    sys.exit()
                digest_stream(data.decode(), self.state)
            self.lock.release()
            self.c_sock.close()
            sys.exit(0)


        def digest_stream(self, data_string, state_flag):
            global TOKEN
            global file_
            global state
            if TOKEN+TOKEN in data_string: #Handle the empty file.
                #print('Received TOKEN|TOKEN')
                if state_flag is 'd':
                    #print('Empty file')
                    #print('[[Closing file]]')
                    os.close(self.file_fd)
                    self.state = 'f'
            elif state_flag is 'f':
                #print('[[State Flag is f]]')
                if TOKEN in data_string:
                    #print('[[Token. Adding to filename then openning.]]')
                    i = data_string.index(TOKEN)
                    #print('Token index is: %d' % i)
                    add_to_filename(data_string[0:i])
                    open_file_descriptor()
                    #print('[[Calling digest stream w/ d]]')
                    self.state = 'd'
                    digest_stream(data_string[i + 1:], self.state)
                else:
                    #print('[[No token. Adding to Filename. State flag is:]] %s' % state_flag)
                    add_to_filename(data_string)
            elif state_flag is 'd':
                #print('[[State Flag is d]]')
                if TOKEN in data_string:
                    #print('[[Token exists with d]]')
                    i = data_string.index(TOKEN)
                    write_to_file(data_string(data_string[:i]))
                    #print('[[Closing file:]] %s' % filename)
                    os.close(self.file_fd)
                    self.state = 'f'
                    digest_stream(data_string[i + 1,], self.state)
                else:
                    #print('[[No token with d]]')
                    write_to_file(data_string)
            else:
                raise Exception('Cannot digest stream. unrecognized state flag: %s'
                                % state_flag)


        def add_to_filename(filename_string):
            #print('[[Adding to filename]]: (%s)' % filename_string)
            global filename
            filename += filename_string


        def open_file_descriptor():
            #print('[[Openning file descriptor]]: (%s)' % filename)
            if os.path.isfile(self.filename):
                f_split = filename.split('.')
                file_part = f_split[0]
                f_split[0] = file_part + '_copy'
                self.filename = '.'.join(f_split)
            self.file_fd = os.open(self.filename, os.O_WRONLY | os.O_CREAT)
            #print('[[File is openned.]]')


        def write_to_file(data_string):
            #print('[[Writing to file]]')
            os.write(self.file_fd, data_string.encode())

main()
