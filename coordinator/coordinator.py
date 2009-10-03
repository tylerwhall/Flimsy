#!/usr/bin/python

from twisted.internet import glib2reactor
glib2reactor.install()
from twisted.internet import reactor
from twisted.internet import task
from twisted.web.xmlrpc import Proxy
import glib

from serial import Serial
import sensormesh

class ServerCommunicator:
    def __init__(self, server_address):
        self.version = 0.1
        self.version_match = False
        self.proxy = Proxy(server_address)
        self.get_version()

    def get_version(self):
        self.proxy.callRemote('version').addCallbacks(self.version_return, self.printError)

    def version_return(self, value):
        if value == self.version:
            print "Server protocol version validated"
            self.version_match = True
        else:
            print "Version mismatch. Wanted: ", self.version, "Got:", value
            reactor.stop()

    def update_sensor(self, id, value):
        if self.version_match:
            print "update sensor"
            self.proxy.callRemote('update_sensor', id, value).addCallbacks(self.update_success, self.printError)
        else:
            self.get_version()

    def update_success(self, value):
        if value:
            print "Update success"

    def printError(self, error):
        print 'error', error

def main():
    def ser_cb(*args):
        x.recv(ser.read())
        return True

    s = ServerCommunicator('http://localhost:5000')
    x = sensormesh.XbeeSensorMesh()
    x.sensor_cb = s.update_sensor
    ser = Serial("/dev/ttyACM0", 9600, timeout=0)
    ser.read()
    glib.io_add_watch(ser, glib.IO_IN, ser_cb)
    reactor.run()

if __name__ == "__main__":
    main()
