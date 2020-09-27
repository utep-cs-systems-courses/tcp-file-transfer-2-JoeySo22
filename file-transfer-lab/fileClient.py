#! /usr/bin/env python3

'''
Author: Jose Eduardo Soto

Description: This is the client module for the file tranfering program.
'''

import socket as sock
import sys, os

sys.path.append('../lib')
import params

def main():
    list_of_files = get_files_from_arguments(sys.argv)

    switches = ((('-s', '--server'), 'server', '127.0.0.1:50001'),
                (('-?', '--usage'), 'usage', False),
                (('-f', '--files'), 'files', list_of_files))
    program_name = 'fileClient.py'
    param_map = params.parseParams(switches)

    server, usage = param_map['server'], param_map['usage']

    if usage:
        params.usage()

    server_ip, server_port = re.split(':', server)
    server_port = int(server_port)

    DATA_SIZE = 80 #79 + newline. From pep8
    START_FILE = '***START***'
    FINISH_FILE = '***FINISH***'
    START_SESSION = '***SESSION_START***' # Longest: 19
    FINISH_SESSION = '***SESSION_OVER***'
    SUCCESS = '***SUCCESS***'
    FAILURE = '***FAILURE***'
    GIVE_DATA = '***GIVE_DATA***'

    file_descriptors = []
    for f in list_of_files:
        try:
            '''
            This must become a tuple so that server can understand the
            name of the file and the file descriptor. Each element in
            file_descriptors is (fd, filename string)
            '''
            file_descriptors.extend((os.open(f, os.O_RDONLY), f))
        except:
            os.write(1, ('Error: Cannot open file %s\n' % f).encode()) # Fail

    '''
    Clients need IC which stands for initiate & connect.
    '''
    cl_sock = sock.socket(sock.AF_INET, sock.SOCK_STREAM) #ipv4 & tcp settings
    cl_sock.connect((server_ip, server_port)) # Connect to server

    client_fd = cl_sock.fileno() #Will use file_descriptor of socket. 
    for f_fd in file_descriptors:
        file_desc, file_name = f_fd
        os.write(client_fd, ('$$$%s$$$' % file_name).encode())
        #Need a way to send the name of the file so that the client expects it.

        mini_buff = os.read(f_fd, DATA_SIZE) #Good linelength format. From py books
        while mini_buff:
            os.write(client_fd, mini_buff)
        os.write(client_fd, FINISH_FILE.encode()) #File is finished message to Server
    os.write(client_fd, FINISH_SESSION.encode())#Session is finished


'''
Given the entire sys.argv data, find out what all intended filenames are.
'''
def get_filenames_from_arguments(arguments):
    list_of_files = []
    if '-f' in a:
        os.write(1, 'Found [-f]\n'.encode())
        _f_index = a.index('-f')
        list_of_files.extend(a[_f_index + 1: find_end_of_flag(
            a[_f_index + 1:], len(a))])
    elif '--files' in a:
        os.write(1, 'Found [--files]\n'.encode())
        _files_index = a.index('--files')
        list_of_files.extend(a[_files_index + 1: find_end_of_flag(
            a[_files_index + 1:], len(a))])
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
