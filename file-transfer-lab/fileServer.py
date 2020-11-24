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
current_file_list = []

def main():
    #Servers need IBLA, which stands for initiate, bind, listen, and accept.
    s_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #ipv4 and tcp settings
    s_sock.bind((listening_addr, listening_port))
    s_sock.listen(1)

    while True:
        os.write(1, 'Listening for clients\n'.encode())
        try:
            client_sock, client_addr = s_sock.accept()
            client_thread = TCPClientSession(client_sock, client_addr)
            os.write(1, 'captured client.\n'.encode())
            client_thread.start()
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
            self.check_filename_lock = threading.Lock()
            self.c_sock = client_socket
            self.c_addr = client_address
            self.client_sock_fd = self.c_sock.fileno()
            self.client_ip, self.client_port = self.c_addr
            self.filename = ''
            self.file_fd = None
            self.state = 'f'
            print('%s created.' % self.name)


        #Inherited Thread method. Does receiving and writing logic here.
        def run(self):
            print('%s is running.' % self.name)
            global DATA_SIZE
            #self.lock.acquire() implementing lower lock
            working = True
            while working:
                #print('[[Reading from socket]]')
                data = os.read(self.client_sock_fd, DATA_SIZE)
                if data is b'':
                    break
                self.digest_stream(data.decode(), self.state)
            #self.lock.release() implementing lower lock
            print('%s finished.' % self.name)
            self.c_sock.close()
            sys.exit(0)


        def digest_stream(self, data_string, state_flag):
            #print('Data recieved %s' % data_string)
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
                    self.add_to_filename(data_string[0:i])
                    '''
                    Here we will check if the filename exists.
                    What kind of behavior should it have?
                    Throw an exception.
                    '''
                    self.check_filename()
                    self.open_file_descriptor()
                    #print('[[Calling digest stream w/ d]]')
                    self.state = 'd'
                    self.digest_stream(data_string[i + 1:], self.state)
                else:
                    #print('[[No token. Adding to Filename. State flag is:]] %s' % state_flag)
                    self.add_to_filename(data_string)
            elif state_flag is 'd':
                #print('[[State Flag is d]]')
                if TOKEN in data_string:
                    #print('[[Token exists with d]]')
                    i = data_string.index(TOKEN)
                    self.write_to_file(data_string(data_string[:i]))
                    #print('[[Closing file:]] %s' % filename)
                    os.close(self.file_fd)
                    self.state = 'f'
                    self.digest_stream(data_string[i + 1,], self.state)
                else:
                    #print('[[No token with d]]')
                    self.write_to_file(data_string)
            else:
                raise Exception('Cannot digest stream. unrecognized state flag: %s'
                                % state_flag)

        def check_filename(self):
            '''
            If the filename already exists in our workload then it should close the connection and kill that job.
            if the filename doesn't exist, then continue.
            '''
            global current_file_list
            self.check_filename_lock.acquire()
            if self.filename in current_file_list:
                raise Exception('%s is already being uploaded.' % self.filename)
            self.check_filename_lock.release()


        def add_to_filename(self, filename_string):
            #print('[[Adding to filename]]: (%s)' % filename_string)
            self.filename += filename_string


        def open_file_descriptor(self):
            #print('[[Openning file descriptor]]: (%s)' % filename)
            if os.path.isfile(self.filename):
                f_split = self.filename.split('.')
                file_part = f_split[0]
                f_split[0] = file_part + '_copy'
                self.filename = '.'.join(f_split)
            #print('%s is filename.' % self.filename)
            self.file_fd = os.open(self.filename, os.O_WRONLY | os.O_CREAT)
            #print('[[File is openned.]]')


        def write_to_file(self, data_string):
            #print('[[Writing to file]]')
            self.lock.acquire()
            os.write(self.file_fd, data_string.encode())
            self.lock.release()



main()

