#!/usr/bin/python

from threading import Timer
from xbee import Xbee

class SensorMesh(object):
    """Base class for a sensor mesh.  This simply lets clients set a callback
    function"""
    def __init__(self):
        self.sensor_cb = None
    def notify(self, num, value):
        if self.sensor_cb:
            self.sensor_cb(num, value)

class XbeeSensorMesh(SensorMesh):
    """Creates a new Xbee instance and registers with the digital callback.
    When a digital reading comes in, it uses the "sensors" dictionary to map
    Xbee addresses to web server sensor ids"""
    def __init__(self, sensors):
        super(XbeeSensorMesh, self).__init__()
        self.xbee = Xbee()
        self.xbee.dig_cb = self.dig_cb
        self.sensors = sensors

    def dig_cb(self, addr, network, pin, value):
        try:
            if pin == 0:
                num = self.sensors[addr]
                if self.sensor_cb:
                    self.sensor_cb(num, not value) #Invert for active low port
        except KeyError:
            print "Got reading from unknown sensor 0x%x" % addr

    def recv(self, data):
        """Eats input data from the Xbee module and generates events"""
        self.xbee.recv(data)

class FakeSensorMesh(SensorMesh):
    """Externally equivalent to the XbeeSensorMesh.  Currently reports false for
    each sensor in the provided list of sensor ids"""
    def __init__(self, ids):
        super(FakeSensorMesh, self).__init__()
        self.ids = ids

    def start(self):
        """Starts the event generator thread"""
        t = Timer(3, self.timer_pop)
        t.start()

    def timer_pop(self):
        for id in self.ids:
            self.notify(id, False)
        self.start()
    
def main():
    import serial
    def print_sensor(num, value):
        print "Sensor", num, value
    s = serial.Serial('/dev/ttyACM0', 9600)
    c = XbeeSensorMesh()
    c.sensor_cb = print_sensor
    f = FakeSensorMesh([1,2,3])
    f.sensor_cb = print_sensor
    f.start()
    while True:
        c.recv(s.read())

if __name__ == "__main__":
    main()
