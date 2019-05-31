import socket
import sys

import serial, time

SERIALPORT = "/dev/ttyUSB0"
BAUDRATE = 9600
OFF = "Off"
ON = "On"

CR = '\r'
LF = '\n'

LightState = [OFF, OFF, OFF]

def SimulateSerialResponse(connection, input):
    if len(input) == 9:
        if input[6].isdigit() and int(input[6] <= len(LightState)):
            if input[7] == '?':
                connection.send(LF + 'Complete' + CR + LF + \
                    'Plug ' + input[6] + ' ' + LightState[int(input[6])] + CR)
                return
        elif input[7].isdigit():
            if input[7] == '0':
                LightState[int(input[6])] = OFF
            elif input[7] == '1':
                LightState[int(input[6])] = OFF
            else:
                print 'Invalid on/off state: "' + input + '"'
                return
            print 'Light ' + input[6] + " turned " + LightState[int(input[6])]
            return
    
    print 'Invalid input message: "' + input + '"'
    
ser = serial.Serial(SERIALPORT, BAUDRATE)
ser.bytesize = serial.EIGHTBITS     # number of bits per bytes
ser.parity = serial.PARITY_NONE     # set parity check: no parity
ser.stopbits = serial.STOPBITS_ONE  # number of stop bits
#ser.timeout = None                 # block read
#ser.timeout = 0                    # non-block read
ser.timeout = 2                     # timeout block read
ser.xonxoff = False                 # disable software flow control
ser.rtscts = False                  # disable hardware (RTS/CTS) flow control
ser.dsrdtr = False                  # disable hardware (DSR/DTR) flow control
ser.writeTimeout = 0                # timeout for write

print >>sys.stderr, 'Starting Up Serial Monitor'

try:
    if(ser.isOpen() == False):
        ser.open()

except Exception, e:
    print >>sys.stderr, "error open serial port: " + str(e)
    exit(1)

if ser.isOpen():

    try:
        ser.flushInput()            # flush input buffer, discarding all its contents
        ser.flushOutput()           # flush output buffer, aborting current output

    except Exception, e:
        print >>sys.stderr, "error communicating...: " + str(e)

else:
    print >>sys.stderr, "cannot open serial port "
    exit(1)

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
                    if char == LF:              # Ignore line feed characters
                        continue

                    else:
                        input = input + char    # Append this character onto input
                    
                        if char == CR:          # Send input out serial port
                            print >>sys.stderr, 'Command received "%s"' % ':'.join('{:02x}'.format(ord(c)) for c in input)
                            print >>sys.stderr, "%d bytes writen to port %s" % (ser.write(input), SERIALPORT)
                            SimulateSerialResponse(connection, input)
                            input = ''          # Reset input buffer

            else:
                print >>sys.stderr, 'no more data from', client_address
                break
            
    finally:
        # Clean up the connection
        connection.close()
