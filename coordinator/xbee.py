#!/usr/bin/python
import struct

class Xbee:
    def __init__(self):
        if struct.calcsize('Q') != 8:
            raise Exception('sizeof() error')
        self.state = 0
        self.state_esc = False
        self.recv_cb = None
        self.write_cb = None
        self.dig_cb = None
        self.adc_cb = None
        self.current_frame = 1
        self.frame_cbs = {}

    def frame_inc(self):
        self.current_frame = (self.current_frame % 255) + 1

    def call_frame_cb(self, frame, *args):
        try:
            if self.frame_cbs[frame][0] is not None:
                self.frame_cbs[frame][0](self.frame_cbs[frame][1], *args)
        except KeyError:
            print "Got callback for unknown frame"

    def buf_to_val(self, data):
        """Convert a string of bytes to a value (big endian)"""
        val = 0
        for i in range(len(data)):
            val += ord(data[i]) * 2**((len(data)-1-i)*8)
        return val

    def checksum(self, data):
        """Calculate the xbee checksum of a string of bytes"""
        checksum = 0
        for byte in data:
            checksum += ord(byte)
        checksum %= 256
        return 0xff - checksum

    def at_command_remote(self, addr, network, data, queued=False, cb=None, arg=None):
        """Send a command to a remote Xbee"""
        packet = [chr(0x17)]
        packet.append(chr(self.current_frame)) #Frame ID
        self.frame_cbs[self.current_frame] = (cb, arg) #Store callback for response
        self.frame_inc() #Increment frame number
        packet.append(struct.pack('!Q', addr)) #Destination address
        packet.append(struct.pack('!H', network)) #Network address (doesn't matter for DM)
        if queued:
            packet.append(chr(0x0))
        else:
            packet.append(chr(0x2))
        packet.append(data)
        self.send_frame("".join(packet))

    def at_command(self, data=None, queued=False, cb=None, arg=None):
        """ Send a local at command """
        if queued: #API identifier
            packet = [chr(0x09)]
        else:
            packet = [chr(0x08)]
        packet.append(chr(self.current_frame)) #Frame ID
        self.frame_cbs[self.current_frame] = (cb, arg) #Store callback for response
        self.frame_inc() #Increment frame number
        packet.append(data)
        self.send_frame("".join(packet))

    def escape_packet(self, data):
        packet = []
        packet.append(data[0])
        for byte in data[1:]:
            ibyte = ord(byte)
            if ibyte in (0x7e,0x7d,0x11,0x13):
                packet.append(chr(0x7d))
                packet.append(chr(ibyte^0x20))
            else:
                packet.append(byte)
        return "".join(packet)

    def transmit(self, addr, network, data):
        packet = [chr(0x10)] #API identifier
        packet.append(chr(0)) #Frame ID
        packet.append(struct.pack('!Q', addr)) #Destination address
        packet.append(struct.pack('!H', network)) #Network address (doesn't matter for DM)
        packet.append(chr(0)) #Broadcast radius (always 0)
        packet.append(chr(0)) #Unicast
        packet.append(data) #Payload
        packet = "".join(packet)
        packet = self.escape_packet(packet)
        self.send_frame(packet)

    def send_frame(self, data):
        frame = chr(0x7e) # Start delimiter
        frame += chr(int(len(data) / 256)) #MSB of len
        frame += chr(int(len(data) % 256)) #LSB of len
        frame += data
        frame += chr(self.checksum(data))
        if self.write_cb:
            self.write_cb(frame)

    def handle_recv(self, data):
        addr = self.buf_to_val(data[:8])
        network = self.buf_to_val(data[8:10])
        broadcast = ord(data[10]) == 2
        packet = data[11:]
        if self.recv_cb:
            self.recv_cb(addr, network, broadcast, packet)

    def handle_at(self, data):
        frame = ord(data[0])
        name = data[1:3]
        status = ord(data[3])
        data = data[4:]
        self.call_frame_cb(frame, name, status, data)
        
    def handle_remote_at(self, data):
        frame = ord(data[0])
        addr = self.buf_to_val(data[1:9])
        network = self.buf_to_val(data[9:11])
        name = data[11:13]
        status = ord(data[13])
        data = data[14:]
        self.call_frame_cb(frame, name, status, data)

    def handle_transmit_status(self, data):
        frame = ord(data[0])
        network = self.buf_to_val(data[1:3])
        retry_count = ord(data[3])
        delivery_status = ord(data[4])
        discovery_status = ord(data[5])
        print "Transmit status:"
        print "network=", network
        print "retry_count=", retry_count
        print "delivery_status=", delivery_status
        print "discovery_status=", discovery_status

    def handle_remote_io(self, data):
        addr = self.buf_to_val(data[0:8])
        network = self.buf_to_val(data[8:10])
        dig_enb = self.buf_to_val(data[12:14])
        adc_enb = self.buf_to_val(data[14])
        dig_dat = self.buf_to_val(data[15:17])
        data = data[17:]
        for i in range(8):
            if dig_enb & 0x1:
                if self.dig_cb:
                    self.dig_cb(addr, network, i, (dig_dat & 0x1) == 1)
            dig_dat >>= 1
            dig_enb >>=1
        for i in range(5):
            if adc_enb & 0x1:
                val = self.buf_to_val(data[0:2])
                data = data[2:]
                if self.adc_cb:
                    self.adc_cb(addr, network, i, val)
            adc_enb >>=1

    def handle_incoming_packet(self, data):
        id = ord(data[0])
        data = data[1:]
        if id == 0x90: #Recv
            self.handle_recv(data)
        elif id == 0x88: #AT response
            self.handle_at(data)
        elif id == 0x97: #Remote AT response
            self.handle_remote_at(data)
        elif id == 0x8b:
            self.handle_transmit_status(data)
        elif id == 0x92:
            self.handle_remote_io(data)
        else:
            print "Unhandled packet type.  id = 0x%x" % id

    def recv(self, data):
        """ Parse incoming serial data and generate events """
        for byte in data:
            if ord(byte) == 0x7e: #Look for start delimiter
                self.state = 1
                continue
            elif ord(byte) == 0x7d:
                self.state_esc = True
                continue
            elif self.state_esc == True:
                self.state_esc = False
                byte = chr(ord(byte)^0x20)
            if self.state == 1: #MSB of len
                self.recv_len = ord(byte) * 256
                self.state += 1
            elif self.state == 2: #LSB of len
                self.recv_len += ord(byte)
                self.recv_data = []
                self.recv_chksum = 0
                self.state += 1
            elif self.state == 3: #Data
                self.recv_data.append(byte)
                self.recv_len -= 1
                if self.recv_len == 0:
                    self.recv_data = "".join(self.recv_data)
                    self.state += 1
            elif self.state == 4: #Checksum
                self.state = 0
                chk = self.checksum(self.recv_data)
                if chk == ord(byte):
                    self.handle_incoming_packet(self.recv_data)
                else:
                    print "Checksum failed. Wanted 0x%x Got 0x%x" % (chk, ord(byte))

if __name__ == "__main__":
    def write(data):
        ser.write(data)
        def recv(*args):
            print "Got rx packet"
        print args

    def remote_digital_cb(addr, network, pin, value):
        print "Addr", addr, "Pin", pin, "=", value
        x.at_command_remote(0x13a2004032d957, 0xfffe, "D1" + chr(0x5))
        x.at_command_remote(0x13a2004032d957, 0xfffe, "D1" + chr(0x4))

    def remote_analog_cb(addr, network, pin, value):
        print "Addr", addr, "ADC", pin, "=", value

    def remote_at_cb(led, name, status, data):
        print "Got remote AT response"
        print "Status = 0x%x" % status
        led += 1
        led %= 2
        x.at_command_remote(addr, 0xfffe, "D0" + chr(0x4 + led), cb=remote_at_cb, arg=led)

    import serial
    ser = serial.Serial('/dev/ttyACM0', 9600)
    addr = 0x13a2004032d957
    x = Xbee()
    x.recv_cb = recv
    x.write_cb = write
    x.dig_cb = remote_digital_cb
    x.adc_cb = remote_analog_cb
    led = 1
    x.transmit(0xffff, 0xfffe, "Hello World\r")
    #remote_at_cb(1, None, 0, None)
    while True:
        x.recv(ser.read())

