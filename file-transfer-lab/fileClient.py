#! /usr/bin/env python3

'''
Author: Jose Eduardo Soto

Description: This is the client module for the file tranfering program.
'''

import socket as sock
import re, sys, os

'''sys.path.append('../lib')
import params '''

def main():
    list_of_files = get_filenames_from_arguments(sys.argv)

    '''switches = ((('-s', '--server'), 'server', '127.0.0.1:50001'),
                (('-?', '--usage'), 'usage', False),
                (('-f', '--files'), 'files', list_of_files))
    program_name = 'fileClient'
    param_map = params.parseParams(switches)

    server, usage = param_map['server'], param_map['usage']

    if usage:
        params.usage()'''

    server_ip, server_port = '127.0.0.1', '50001'
    server_port = int(server_port)

    DATA_SIZE = 80 #79 + newline. From pep8
    TOKEN = '\0'

    file_tuple = []
    for f in list_of_files:
        try:
            '''
            This must become a tuple so that server can understand the
            name of the file and the file descriptor. Each element in
            file_descriptors is (fd, filename string)
            '''
            file_tuple.append(tuple((os.open(f, os.O_RDONLY), f)))
        except:
            os.write(1, ('Error: Cannot open file %s\n' % f).encode()) # Fail

    '''
    Clients need IC which stands for initiate & connect.
    '''
    cl_sock = sock.socket(sock.AF_INET, sock.SOCK_STREAM) #ipv4 & tcp settings
    cl_sock.connect((server_ip, server_port)) # Connect to server

    client_fd = cl_sock.fileno() #Will use file_descriptor of socket.
    print('Number of file descriptors: %d' % len(file_tuple))
    for f in file_tuple:
        file_desc, file_name = f
        print('Filename is: %s' % file_name)
        #print('Sending NULL token')
        #os.write(client_fd, TOKEN.encode())
        print('Sending: %s' % file_name)
        os.write(client_fd, file_name.encode())
        print('Sending NULL token')
        os.write(client_fd, TOKEN.encode())
        mini_buff = os.read(file_desc, DATA_SIZE) #Good linelength format. From py books
        while mini_buff:
            os.write(client_fd, mini_buff)
            print('Sending: %s' % mini_buff.decode())
            mini_buff = os.read(file_desc, DATA_SIZE)
        os.close(file_desc)
    os.close(client_fd)


'''
Given the entire sys.argv data, find out what all intended filenames are.
'''
def get_filenames_from_arguments(arguments):
    list_of_files = []
    if '-f' in arguments:
        os.write(1, 'Found [-f]\n'.encode())
        _f_index = arguments.index('-f')
        list_of_files.extend(arguments[_f_index + 1: find_end_of_flag(
            arguments[_f_index + 1:], len(arguments))])
    elif '--files' in arguments:
        os.write(1, 'Found [--files]\n'.encode())
        _files_index = arguments.index('--files')
        list_of_files.extend(arguments[_files_index + 1: find_end_of_flag(
            arguments[_files_index + 1:], len(arguments))])
    else:
        os.write(1, b'Error: There is no file input\n')
        sys.exit(-1)
    return list_of_files


'''
Returns the index of the end of the argument by finding the next flag. If there
are no other flags then return the length of the list.
''' 
def find_end_of_flag(argument_list, len_of_o_list):
    os.write(1, ('The arguement received was: [%s]\n' %argument_list).encode())
    for element in argument_list:
        if '-' in element:
            end_of_flag = argument_list.index(element)
            return end_of_flag + (len_of_o_list - end_of_flag) - 1
    return len_of_o_list


main()
