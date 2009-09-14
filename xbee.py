#!/usr/bin/python
import serial
import struct

class Xbee:
    def __init__(self, serial):
        if struct.calcsize('Q') != 8:
            raise Exception('sizeof() error')
        self.serial = serial
        self.state = 0
        self.recv_cb = None
        self.current_frame = 1
        self.frame_cbs = {}

    def frame_inc(self):
        self.current_frame = (self.current_frame % 255) + 1

    def call_frame_cb(self, frame, *args):
        if self.frame_cbs[frame][0] is not None:
            self.frame_cbs[frame][0](self.frame_cbs[frame][1], *args)

    def buf_to_val(self, data):
        val = 0
        for i in range(len(data)):
            val += ord(data[i]) * 2**((len(data)-1-i)*8)
        return val

    def checksum(self, data):
        checksum = 0
        for byte in data:
            checksum += ord(byte)
        checksum %= 256
        return 0xff - checksum

    def at_command_remote(self, addr, network, data, queued=False, cb=None, arg=None):
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

    #Data: String of AT data
    #Queued: Boolean
    def at_command(self, data=None, queued=False, cb=None, arg=None):
        if queued: #API identifier
            packet = [chr(0x09)]
        else:
            packet = [chr(0x08)]
        packet.append(chr(self.current_frame)) #Frame ID
        self.frame_cbs[self.current_frame] = (cb, arg) #Store callback for response
        self.frame_inc() #Increment frame number
        packet.append(data)
        self.send_frame("".join(packet))

    def transmit(self, addr, network, data):
        packet = [chr(0x10)] #API identifier
        packet.append(chr(0)) #Frame ID
        packet.append(struct.pack('!Q', addr)) #Destination address
        packet.append(struct.pack('!H', network)) #Network address (doesn't matter for DM)
        packet.append(chr(0)) #Broadcast radius (always 0)
        packet.append(chr(0)) #Unicast
        packet.append(data) #Payload
        self.send_frame("".join(packet))

    def send_frame(self, data):
        frame = chr(0x7e) # Start delimiter
        frame += chr(int(len(data) / 256)) #MSB of len
        frame += chr(int(len(data) % 256)) #LSB of len
        frame += data
        frame += chr(self.checksum(data))
        self.serial.write(frame)

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
        else:
            print "Unhandled packet type.  id = 0x%x" % id

    def recv(self, data):
        for byte in data:
            if self.state == 0: #Look for start delimiter
                if ord(byte) == 0x7e:
                    self.state += 1
            elif self.state == 1: #MSB of len
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

def recv(*args):
    print "Got rx packet"
    print args


def remote_at_cb(led, name, status, data):
    print "Got remote AT response"
    print "Status = 0x%x" % status
    led += 1
    led %= 2
    x.at_command_remote(addr, 0xfffe, "D0" + chr(0x4 + led), cb=remote_at_cb, arg=led)

if __name__ == "__main__":
    ser = serial.Serial('/dev/ttyACM0', 9600)
    addr = 0x13a2004032d957
    x = Xbee(ser)
    x.recv_cb = recv
    led = 1
    #x.transmit(0xffff, 0xfffe, "Hello World\r\n")
    remote_at_cb(1, None, 0, None)
    while True:
        x.recv(ser.read())
