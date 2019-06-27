""" Read input from a USB serial port and simulate a BlackBox Pow-R-Switch IR
    power switching device and return any simulated respone back out the same
    USB serial port.
"""
import sys
import datetime
import serial


SERIALPORT = "/dev/ttyUSB1"
BAUDRATE = 9600
OFF = "Off"
ON = "On"

CR = '\r'
LF = '\n'


def timestamp():
    """
    Print the current time as a timestamp to sys.stderr
    """
    # When running as a service we no longer need a timestamp
    if false:
        current_time = datetime.datetime.now()
        print >>sys.stderr, current_time.strftime("%Y-%m-%d-%H:%M:%S.%f:"),


def simulate_serial_response(in_serial, in_input, in_light_state):
    """ Simulate a BlackBox Pow-R-Switch IR power switching device
    by analyzing input and return correct simulated respone back out the
    USB serial port.
    """
    if len(in_input) == 9:
        if in_input[6].isdigit() and int(in_input[6]) <= len(in_light_state)-1:
            if in_input[7] == '?':
                in_serial.write(LF + 'Complete' + CR + LF + \
                    'Plug ' + in_input[6] + ' ' + in_light_state[int(in_input[6])] + CR)
                return

            elif in_input[7].isdigit():
                if in_input[7] == '0':
                    in_light_state[int(in_input[6])] = OFF
                elif in_input[7] == '1':
                    in_light_state[int(in_input[6])] = ON
                else:
                    timestamp()
                    print >>sys.stderr, 'Invalid on/off state: "' + in_input + '"'
                    return

                timestamp()
                print >>sys.stderr, 'Light ' + in_input[6] \
                    + " turned " + in_light_state[int(in_input[6])]
                return
            else:
                timestamp()
                print >>sys.stderr, '8th character is not a digit or question mark'
        else:
            timestamp()
            print >>sys.stderr, '7th character is not a digit or out of range'
    else:
        timestamp()
        print >>sys.stderr, 'Input is not 9 characters'

    timestamp()
    print >>sys.stderr, 'Invalid input message: "' + in_input + '"'

def blue_light_tcp_2_serial():
    """ Read input from a USB serial port and simulate a BlackBox Pow-R-Switch IR
    power switching device and return any simulated respone back out the same
    USB serial port.
    """
    ser = serial.Serial(SERIALPORT, BAUDRATE)
    ser.bytesize = serial.EIGHTBITS     # number of bits per bytes
    ser.parity = serial.PARITY_NONE     # set parity check: no parity
    ser.stopbits = serial.STOPBITS_ONE  # number of stop bits
    #ser.timeout = None                 # block read
    #ser.timeout = 0                    # non-block read
    ser.timeout = 0.2                   # timeout block read in seconds
    ser.xonxoff = False                 # disable software flow control
    ser.rtscts = False                  # disable hardware (RTS/CTS) flow control
    ser.dsrdtr = False                  # disable hardware (DSR/DTR) flow control
    ser.writeTimeout = None             # timeout for write - None => non-blocking

    light_state = [OFF, OFF, OFF]

    timestamp()
    print >>sys.stderr, 'Starting up Blue Light Simulator'

    if ser.isOpen() is False:
        ser.open()

    if ser.isOpen():
        ser.flushInput()            # flush input buffer, discarding all its contents
        ser.flushOutput()           # flush output buffer, aborting current output

    else:
        timestamp()
        print >>sys.stderr, "cannot open serial port "
        exit(1)

    input_so_far = ''
    while True:
        # Wait for input - Timeout is set to 0.2 seconds

        data = ser.read(128)        # Read up to 128 bytes

        if data:
            timestamp()
            print >>sys.stderr, 'received "%s"' % ':'.join('{:02x}'.format(ord(c)) for c in data)
            for char in data:
                if char == LF:      # Ignore line feed characters
                    continue

                else:
                    input_so_far = input_so_far + char  # Append this character onto input

                    if char == CR:  # Send input out serial port
                        timestamp()
                        print >>sys.stderr, 'Command received "%s"' % ':' \
                            .join('{:02x}'.format(ord(c)) for c in input_so_far)
                        simulate_serial_response(ser, input_so_far, light_state)
                        input_so_far = ''               # Reset input buffer

if __name__ == '__main__':
    blue_light_tcp_2_serial()
