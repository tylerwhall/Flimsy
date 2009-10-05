#!/usr/bin/python

import glib

from serial import Serial
import httplib
import urllib
import sensormesh

class ServerCommunicator:
    def __init__(self, server_address):
        self.server = server_address

    def update_sensor(self, id, value):
        con = httplib.HTTPConnection(self.server)
        con.connect()
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        params = urllib.urlencode({"id": id, "flooded": value})
        con.request("POST", "/map/update",params,headers)
        res = con.getresponse()
        print res.read()
        print res.status, res.reason

    def update_success(self, value):
        if value:
            print "Update success"

    def printError(self, error):
        print 'error', error

def main():
    def ser_cb(*args):
        x.recv(ser.read())
        return True

    s = ServerCommunicator('127.0.0.1:8080')
    x = sensormesh.XbeeSensorMesh()
    x.sensor_cb = s.update_sensor
    ser = Serial("/dev/ttyACM0", 9600, timeout=0)
    ser.read()
    glib.io_add_watch(ser, glib.IO_IN, ser_cb)
    glib.MainLoop().run()

if __name__ == "__main__":
    main()
