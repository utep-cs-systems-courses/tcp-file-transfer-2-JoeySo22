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

DATA_SIZE = 80 # 79 + newline
START_FILE = '***START***'
FINISH_FILE = '***FINISH***'
START_SESSION = '***SESSION_START***' # Longest: 19
FINISH_SESSION = '***SESSION_OVER***'
SUCCESS = '***SUCCESS***'
FAILURE = '***FAILURE***'
GIVE_DATA = '***GIVE_DATA***'

def main():
    #Servers need IBLA, which stands for initiate, bind, listen, and accept.
    s_sock = sock.socket(sock.AF_INET, sock.SOCK_STREAM) #ipv4 and tcp settings
    s_sock.bind(listening_addr, listening_port)
    s_sock.listen(1)

    client_sock, client_addr = s_sock.accept()

    working = True
    
    client_sock_fd = client_sock.fileno()
    while working:
        data = client_sock_fd.read(0, DATA_SIZE)
        if data is SESSION_START:
            client_sock_fd.write(1, GIVE_DATA)
        elif data is START:
            
        elif data is FINISH:
        elif data is SESSION_OVER:


main()
