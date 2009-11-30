# -*- coding: utf-8 -*-
"""

"""

from flimsy.tests import TestController
from flimsy.controllers.map import MapController


class TestSensor(TestController):
    """
    Tests for sensor updates
    
    """
    
    application_under_test = 'main'
    
    def test_sensor_update(self):
        """
        Sensor update consistency
        """

        m = MapController()
        out = m.sensors()
        assert not out['sensors'][0]['flooded']
        m.update(id=1,flooded='True')
        out = m.sensors()
        assert out['sensors'][0]['flooded']

