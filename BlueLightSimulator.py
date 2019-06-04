import sys
import serial, time

SERIALPORT = "/dev/ttyUSB1"
BAUDRATE = 9600
OFF = "Off"
ON = "On"

CR = '\r'
LF = '\n'

LightState = [OFF, OFF, OFF]

def SimulateSerialResponse(ser, input):
    if len(input) == 9:
        if input[6].isdigit() and int(input[6]) <= len(LightState)-1:
            if input[7] == '?':
                ser.write(LF + 'Complete' + CR + LF + \
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
    
ser = serial.Serial(SERIALPORT, BAUDRATE)
ser.bytesize = serial.EIGHTBITS     # number of bits per bytes
ser.parity = serial.PARITY_NONE     # set parity check: no parity
ser.stopbits = serial.STOPBITS_ONE  # number of stop bits
#ser.timeout = None                 # block read
#ser.timeout = 0                    # non-block read
ser.timeout = 5                     # timeout block read in seconds
ser.xonxoff = False                 # disable software flow control
ser.rtscts = False                  # disable hardware (RTS/CTS) flow control
ser.dsrdtr = False                  # disable hardware (DSR/DTR) flow control
ser.writeTimeout = None             # timeout for write - None => non-blocking

print >>sys.stderr, 'Starting up Blue Light Simulator'

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

input = ''
while True:
    # Wait for input - Timeout is set to 5 seconds

    data = ser.read()

    if data:
        print >>sys.stderr, 'received "%s"' % ':'.join('{:02x}'.format(ord(c)) for c in data)
        for char in data:
            if char == LF:              # Ignore line feed characters
                continue

            else:
                input = input + char    # Append this character onto input
                    
                if char == CR:          # Send input out serial port
                    print >>sys.stderr, 'Command received "%s"' % ':'.join('{:02x}'.format(ord(c)) for c in input)
                    SimulateSerialResponse(ser, input)
                    input = ''          # Reset input buffer
