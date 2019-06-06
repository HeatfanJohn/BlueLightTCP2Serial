""" Read input from a TCP connection
    and output to a USB Serial port.
"""
import socket
import sys
import serial

SERIALPORT = "/dev/ttyUSB0"
BAUDRATE = 9600
OFF = "Off"
ON = "On"

CR = '\r'
LF = '\n'

def read_from_serial(ser, connection):
    serial_input = ser.read(128)
    if serial_input:
        print >>sys.stderr, 'Serial input "%s"' % ':' \
            .join('{:02x}'.format(ord(c)) for c in serial_input)
        total_sent = 0
        msg_len = len(serial_input)
        while total_sent < msg_len:
            sent = connection.send(serial_input[total_sent:])
            print >>sys.stderr, "sent %d bytes to remote connection" % sent
            if sent == 0:
                raise RuntimeError("socket connection broken")
            total_sent = total_sent + sent


ser = serial.Serial(SERIALPORT, BAUDRATE)
ser.bytesize = serial.EIGHTBITS     # number of bits per bytes
ser.parity = serial.PARITY_NONE     # set parity check: no parity
ser.stopbits = serial.STOPBITS_ONE  # number of stop bits
#ser.timeout = None                 # block read
#ser.timeout = 0                    # non-block read
ser.timeout = 0.2                   # timeout block read
ser.xonxoff = False                 # disable software flow control
ser.rtscts = False                  # disable hardware (RTS/CTS) flow control
ser.dsrdtr = False                  # disable hardware (DSR/DTR) flow control
ser.writeTimeout = 0                # timeout for write

print >>sys.stderr, 'Starting Up Serial Monitor'

if ser.isOpen() is False:
    ser.open()

if ser.isOpen():
    ser.flushInput()                # flush input buffer, discarding all its contents
    ser.flushOutput()               # flush output buffer, aborting current output

else:
    print >>sys.stderr, "cannot open serial port "
    sys.exit(1)

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Then bind() is used to associate the socket with the server address.i
# In this case, the address is localhost, referring to the current server,
# and the port number is 1000.

# Bind the socket to port 1000 on all IPv4 addresses
SERVER_ADDRESS = ('0.0.0.0', 1000)

print >>sys.stderr, 'starting up on %s port %s' % SERVER_ADDRESS
sock.bind(SERVER_ADDRESS)

# Calling listen() puts the socket into server mode,
# and accept() waits for an incoming connection.

# Listen for incoming connections
sock.listen(1)

while True:
    # Wait for a connection
    print >>sys.stderr, 'waiting for a connection'

    # accept() returns an open connection between the server and client

    connection, client_address = sock.accept()
    connection.settimeout(0.2)    # Make non-blocking with 0.2 second timeout
    input = ''
    print >>sys.stderr, 'connection from', client_address

    while True:
        try:
            data = connection.recv(4096)
            print >>sys.stderr, 'received "%s"' % ':'.join('{:02x}'.format(ord(c)) for c in data)
            if data:
                for char in data:
                    if char == LF:              # Ignore line feed characters
                        continue

                    else:
                        input = input + char    # Append this character onto input
                        if char == CR:          # Send input out serial port
                            print >>sys.stderr, 'Command received "%s"' % ':' \
                                .join('{:02x}'.format(ord(c)) for c in input)
                            print >>sys.stderr, \
                                "%d bytes writen to port %s" % (ser.write(input), SERIALPORT)
                            input = ''          # Reset input buffer
            else:
                print >>sys.stderr, 'no more data from', client_address
                # Clean up the connection
                connection.close()
                break

        except socket.timeout:
            read_from_serial(ser, connection)   # Check serial for input and output to TCP

        except socket.error, ex:
            # Something else happened, handle error, exit, etc.
            print >>sys.stderr, ex
            sys.exit(1)
