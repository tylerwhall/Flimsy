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

    @expose('json')
    def update(self, id=1, flooded=False):
        id = int(id)
        try:
            s = DBSession.query(Sensor).filter_by(id=id).one()
        except NoResultFound:
            return str(id) + " not found"
        s.flooded = flooded=='True'
        return "Success", flooded, s.flooded
