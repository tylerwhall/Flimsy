#!/usr/bin/python

import glib

from serial import Serial
import httplib
import urllib
import yaml

import sensormesh

class ServerCommunicator:
    def __init__(self, address, url):
        self.server = address
        self.url = url

    def update_sensor(self, id, value):
        """Send a sensor update to the http server"""
        con = httplib.HTTPConnection(self.server)
        con.connect()
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        params = urllib.urlencode({"id": id, "flooded": value})
        con.request("POST", self.url,params,headers)
        res = con.getresponse()
        print res.read()
        print res.status, res.reason

def main():
    def ser_cb(*args):
        x.recv(ser.read())
        return True

    file = open("config.yaml")
    config = yaml.load(file)
    file.close()
    s = ServerCommunicator(**config['server'])
    x = sensormesh.XbeeSensorMesh(config['sensors'])
    x.sensor_cb = s.update_sensor
    ser = Serial(config['serial_port'], 9600, timeout=0)
    ser.read()
    glib.io_add_watch(ser, glib.IO_IN, ser_cb)
    glib.MainLoop().run()

if __name__ == "__main__":
    main()
