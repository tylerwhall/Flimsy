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

    def at_command_remote(self, addr, network, data, queued=False):
        packet = [chr(0x17)]
        packet.append(chr(0)) #Frame ID
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
    def at_command(self, data=None, queued=False):
        if queued: #API identifier
            packet = [chr(0x09)]
        else:
            packet = [chr(0x08)]
        packet.append(chr(0x0)) #Frame ID
        packet.append(data)
        self.send_frame("".join(packet))

    def transmit(self, addr, network, data):
        packet = [chr(0x10)] #API identifier
        packet.append(chr(1)) #Frame ID
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

    def handle_incoming_packet(self, data):
        id = ord(data[0])
        data = data[1:]
        if id == 0x90: #Recv
            addr = self.buf_to_val(data[:8])
            network = self.buf_to_val(data[8:10])
            broadcast = ord(data[10]) == 2
            packet = data[11:]
            if self.recv_cb:
                self.recv_cb(addr, network, broadcast, packet)
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
    print "Got packet"
    print args

if __name__ == "__main__":
    #ser = serial.Serial('/dev/ttyACM0', 9600)
    ser = open("output.txt", "w")
    x = Xbee(ser)
    x.recv_cb = recv
    #x.transmit(0xffff, 0xfffe, "Hello World\r\n")
    x.at_command("DL")
    exit()
    while True:
        x.recv(ser.read())
