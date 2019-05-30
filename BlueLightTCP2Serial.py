import socket
import sys

CR = '\r'
LF = '\n'

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Then bind() is used to associate the socket with the server address.i
# In this case, the address is localhost, referring to the current server,
# and the port number is 1000.

# Bind the socket to port 1000 on all IPv4 addresses
server_address = ('0.0.0.0', 1000)

print >>sys.stderr, 'starting up on %s port %s' % server_address
sock.bind(server_address)

# Calling listen() puts the socket into server mode,
# and accept() waits for an incoming connection.

# Listen for incoming connections
sock.listen(1)

while True:
    # Wait for a connection
    print >>sys.stderr, 'waiting for a connection'
    connection, client_address = sock.accept()
    input = ''

    # accept() returns an open connection between the server and client,
    # along with the address of the client. The connection is actually a
    # different socket on another port (assigned by the kernel).
    # Data is read from the connection with recv() and transmitted with sendall().

    try:
        print >>sys.stderr, 'connection from', client_address

        while True:
            data = connection.recv(4096)
            print >>sys.stderr, 'received "%s"' % ':'.join('{:02x}'.format(ord(c)) for c in data)
            if data:
                for char in data:
                    if char == LF:
                        continue

                    else:
                        input = input + char
                    
                        if char == CR:
                            print >>sys.stderr, 'Command received "%s"' % ':'.join('{:02x}'.format(ord(c)) for c in input)
                            input = ''

            else:
                print >>sys.stderr, 'no more data from', client_address
                break
            
    finally:
        # Clean up the connection
        connection.close()
