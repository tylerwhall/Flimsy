from tg import expose

from flimsy.lib.base import BaseController

from flimsy.model import DBSession, Sensor
from sqlalchemy import func

class MapController(BaseController):
    @expose('flimsy.templates.map')
    def index(self):
        max = DBSession.query(func.max(Sensor.lat)).one()[0]
        min = DBSession.query(func.min(Sensor.lat)).one()[0]
        lat = (max + min) / 2
        max = DBSession.query(func.max(Sensor.lng)).one()[0]
        min = DBSession.query(func.min(Sensor.lng)).one()[0]
        lng = (max + min) / 2
        return dict(lat=lat, lng=lng)

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

    @expose('json')
    def update(self, id=1, flooded=False):
        id = int(id)
        try:
            s = DBSession.query(Sensor).filter_by(id=id).one()
        except NoResultFound:
            return str(id) + " not found"
        s.flooded = flooded=='True'
        return "Success", flooded, s.flooded
