from tg import expose

from flimsy.lib.base import BaseController

from flimsy.model import DBSession, Sensor

class MapController(BaseController):
    @expose('flimsy.templates.map')
    def index(self):
        return dict()

    @expose('json')
    def sensors(self):
        sens = []
        for row in DBSession.query(Sensor).all():
            s = {}
            s["name"] = row.name
            s["lat"] = row.lat
            s["lng"] = row.lng
            s["flooded"] = row.flooded
            sens.append(s)
        return dict(sensors=sens)
