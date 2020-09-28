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

import os, socket, sys

sys.path.append('../lib')
import params

switchesVarDefaults = ((('-l', '--listenPort'), 'listenPort', 50001),
                       (('-?', '--usage'), 'usage', False),)

progname = 'fileServer'
paramMap = params.parseParams(switchesVarDefaults)

listening_port, listening_addr = paramMap['listenPort'], ''

if paramMap['usage']:
    params.usage()


DATA_SIZE = 80 # 79 + newline
TOKEN = '\0' #I don't know if this extends to other protocals or programs but
# it works for mine. When encoded it is not the same as b'' so its good.

filename = ''
file_fd = None

def main():
    #Servers need IBLA, which stands for initiate, bind, listen, and accept.
    s_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #ipv4 and tcp settings
    s_sock.bind((listening_addr, listening_port))
    s_sock.listen(1)

    os.write(1, 'Listening for clients...'.encode())
    client_sock, client_addr = s_sock.accept()
    os.write(1, ('Got one: %s' % client_addr).encode())

    working = True
    client_sock_fd = client_sock.fileno()
    while working:
        data = os.read(client_sock_fd, DATA_SIZE.encode())
        digest_stream(data.decode())

def digest_stream(data_string, state_flag):
    if TOKEN+TOKEN in data_string: #Handle the empty file.
        if state_flag is 'd':
            os.close(file_fd)
            i = data_string.index(TOKEN)+2
            digest_stream(data_string[i:], 'f')
    if state_flag is 'f':
        if TOKEN in data_string:
            i = data_string.index(TOKEN)
            add_to_filename(data_string[0:i])
            open_file_descriptor()
            digest_stream(data_string[i + 1:], 'd')
        else:
            add_to_filename(data_string)
    elif state_flag is 'd':
        if TOKEN in data_string:
            i = data_string.index(TOKEN)
            write_to_file(data_string(data_string[:i]))
            os.close(file_fd)
            digest_stream(data_string[i + 1,], 'f')
        else:
            write_to_file(data_string)
    else:
        raise Exception('Cannot digest stream. unrecognized state flag: %s'
                        % state_flag)


def add_to_filename(filename_string):
    filename += filename_string


def open_file_descriptor():
    if os.path.isfile(filename):
        f_split = filename.split('.')
        file_part = f_split[0]
        f_split[0] = file_part + '_copy'
        filename = '.'.join(f_split)
    file_fd = os.open(filename, os.O_WRONLY | os.O_CREAT)


def write_to_file(data_string):
    os.write(file_fd, data_string.encode())


main()
