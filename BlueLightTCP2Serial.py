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
        if input[6].isdigit() and int(input[6]) <= len(LightState)-1:
            if input[7] == '?':
                connection.send(LF + 'Complete' + CR + LF + \
                    'Plug ' + input[6] + ' ' + LightState[int(input[6])] + CR)
                return

            elif input[7].isdigit():
                if input[7] == '0':
                    LightState[int(input[6])] = OFF
                elif input[7] == '1':
                    LightState[int(input[6])] = ON
                else:
                    print >>sys.stderr, 'Invalid on/off state: "' + input + '"'
                    return

                print >>sys.stderr, 'Light ' + input[6] + " turned " + LightState[int(input[6])]
                return
            else:
                print >>sys.stderr, '8th character is not a digit or question mark'
        else:
            print >>sys.stderr, '7th character is not a digit or out of range'
    else:
        print >>sys.stderr, 'Input is not 9 characters'
    
    print >>sys.stderr, 'Invalid input message: "' + input + '"'
    
def ReadFromSerial( ser, connection ):
    serialInput = ser.read(128)
    if serialInput:
        print >>sys.stderr, 'Serial input "%s"' % ':'.join('{:02x}'.format(ord(c)) for c in serialInput)
        connection.send( serialInput )
        totalSent = 0
        msgLen = len( serialInput )
        while totalsent < MSGLEN:
            sent = connection.send(msg[totalSent:])
            print >>sys.stderr, "sent %d bytes to remote connection"
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalSent = totalSent + sent


ser = serial.Serial(SERIALPORT, BAUDRATE)
ser.bytesize = serial.EIGHTBITS     # number of bits per bytes
ser.parity = serial.PARITY_NONE     # set parity check: no parity
ser.stopbits = serial.STOPBITS_ONE  # number of stop bits
#ser.timeout = None                 # block read
#ser.timeout = 0                    # non-block read
ser.timeout = 1                     # timeout block read
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
    sys.exit(1)

if ser.isOpen():

    try:
        ser.flushInput()            # flush input buffer, discarding all its contents
        ser.flushOutput()           # flush output buffer, aborting current output

    except Exception, e:
        print >>sys.stderr, "error communicating...: " + str(e)

else:
    print >>sys.stderr, "cannot open serial port "
    sys.exit(1)

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

    # accept() returns an open connection between the server and client

    connection, client_address = sock.accept()
    connection.settimeout(1)    # Make non-blocking with 1 second timeout
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
                            print >>sys.stderr, 'Command received "%s"' % ':'.join('{:02x}'.format(ord(c)) for c in input)
                            print >>sys.stderr, "%d bytes writen to port %s" % (ser.write(input), SERIALPORT)
                            input = ''          # Reset input buffer
            else:
                print >>sys.stderr, 'no more data from', client_address
                # Clean up the connection
                connection.close()
                break

        except socket.timeout, e:
            ReadFromSerial( ser, connection )   # Check serial for input and output to TCP

        except socket.error, e:
            # Something else happened, handle error, exit, etc.
            print >>sys.stderr, e
            sys.exit(1)            

        

