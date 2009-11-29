from sensormesh import *

class TestSensorMesh:
    def setUp(self):
        self.sensormesh = SensorMesh()
        self.success = False

    def callback(self, num, value):
        self.success = True

    def test_notify(self):
        """SensorMesh Notify callback
        
        This is so simple that testing probably causes more problems than it
        fixes.
        
        """
        self.sensormesh.sensor_cb = self.callback
        self.success = False
        self.sensormesh.notify(1, 1)
        assert self.success
