#!/usr/bin/python
import serial

class Xbee:
    def __init__(self, serial):
        self.serial = serial
        self.state = 0

    def checksum(self, data):
        checksum = 0
        for byte in data:
            checksum += ord(byte)
        checksum %= 256
        return 0xff - checksum

    def constructFrame(self, data):
        frame = chr(0x7e) # Start delimiter
        frame += chr(int(len(data) / 8)) #MSB of len
        frame += chr(int(len(data) % 8)) #LSB of len
        frame += data
        frame += chr(self.checksum(data))
        return frame

    def handle_incoming_packet(self, data):
        print "Got a packet"
        for byte in data:
            print "%x" % ord(byte)

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

if __name__ == "__main__":
    ser = serial.Serial('/dev/ttyACM0', 9600)
    x = Xbee(ser)
    while True:
        x.recv(ser.read())
