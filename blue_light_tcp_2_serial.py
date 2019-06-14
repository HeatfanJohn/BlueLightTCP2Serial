""" Bidirectionally read/write date from a TCP connection
    and echo to a USB Serial port.
"""
import os
import datetime
import socket
import sys
import serial

import pygame
from pygame.locals import QUIT

os.environ["SDL_FBDEV"] = "/dev/fb0"    # Use Framebuffer 0

SERIALPORT = "/dev/ttyUSB0"
BAUDRATE = 9600
OFF = "Off"
ON = "On"

CR = '\r'
LF = '\n'

# set up the color constants
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)

# Bind the socket to port 1000 on all IPv4 addresses
SERVER_ADDRESS = ('0.0.0.0', 1000)


def read_from_serial(this_serial, this_connection):
    """
    Read input from our USB serial port and output it
    to the TCP connection currently opened
    """
    serial_input = this_serial.read(128)
    if serial_input:
        print >>sys.stderr, 'Serial input "%s"' % ':' \
            .join('{:02x}'.format(ord(c)) for c in serial_input)
        total_sent = 0
        msg_len = len(serial_input)
        while total_sent < msg_len:
            sent = this_connection.send(serial_input[total_sent:])
            print >>sys.stderr, "sent %d bytes to remote connection" % sent
            if sent == 0:
                raise RuntimeError("socket connection broken")
            total_sent = total_sent + sent

    return serial_input


def change_state(this_input, this_light_state):
    """
    Decode output from serial switch and change state of associated light on/off
    """
    print >>sys.stderr, 'change_state() input "%s"' % this_input
    # Look for "Plug # On/Off" messages
    if len(this_input) in [9, 10] and this_input[0:4] == 'Plug':
        if this_input[5].isdigit() and int(this_input[5]) <= len(this_light_state)-1:
            if this_input[7:9] == 'Of':
                this_light_state[int(this_input[5])] = OFF
            elif this_input[7:9] == 'On':
                this_light_state[int(this_input[5])] = ON
            else:
                print >>sys.stderr, 'Invalid on/off state: "' + this_input + '"'
                return

            print >>sys.stderr, 'Light ' + this_input[5] \
                + " turned " + this_light_state[int(this_input[5])]
            return
        else:
            print >>sys.stderr, 'Input is not a "Plug" message'
    else:
        print >>sys.stderr, 'Input is not 9 or 10 characters'

    print >>sys.stderr, 'Unknown input message: "' + this_input + '"'


def blue_light_tcp_2_serial():
    """ Bidirectionally read/write date from a TCP connection
    and echo to a USB Serial port.
    """

    light_state = [OFF, OFF, OFF]       # Array to maintain state of each light

    pygame.init()

    ## Set up the screen

    display_surface = pygame.display.set_mode((320, 240), 0, 16)
    pygame.mouse.set_visible(0)
    pygame.display.set_caption('BlueLightMonitor')

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
        input_data = ''
        serial_data = ''
        print >>sys.stderr, 'connection from', client_address

        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

            last_time = datetime.datetime.time(datetime.datetime.now())

            try:
                data = connection.recv(4096)
                print >>sys.stderr, 'received "%s"' % ':' \
                    .join('{:02x}'.format(ord(c)) for c in data)
                if data:
                    for char in data:
                        if char == LF:              # Ignore line feed characters
                            continue

                        else:
                            input_data = input_data + char    # Append this character onto input
                            if char == CR:          # Send input out serial port
                                print >>sys.stderr, 'Command received "%s"' % ':' \
                                    .join('{:02x}'.format(ord(c)) for c in input_data)
                                print >>sys.stderr, "%d bytes writen to port %s" \
                                    % (ser.write(input_data), SERIALPORT)
                                input_data = ''          # Reset input buffer
                else:
                    print >>sys.stderr, 'no more data from', client_address
                    # Clean up the connection
                    connection.close()
                    break

            except socket.timeout:
                # Check serial for input and output to TCP
                serial_input = read_from_serial(ser, connection)
                for char in serial_input:
                    if char == LF:              # Ignore line feed characters
                        continue

                    elif char == CR:
                        change_state(serial_data, light_state)
                        serial_data = ''
                    else:
                        serial_data = serial_data + char

                current_time = datetime.datetime.time(datetime.datetime.now())
                if current_time != last_time:
                    ## Draw time
                    last_time = current_time
                    font = pygame.font.Font(None, 75)
                    text = font.render(current_time.strftime("%I:%M:%S %p"), 1, CYAN)
                    textpos = text.get_rect(center=(display_surface.get_width()/2, 215))
                    display_surface.fill(BLACK)
                    display_surface.blit(text, textpos)
                    pygame.display.update()

            except socket.error, ex:
                # Something else happened, handle error, exit, etc.
                print >>sys.stderr, ex
                sys.exit(1)

if __name__ == '__main__':
    blue_light_tcp_2_serial()
