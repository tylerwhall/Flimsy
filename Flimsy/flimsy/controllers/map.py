from tg import expose

from flimsy.lib.base import BaseController

class MapController(BaseController):
    @expose('flimsy.templates.map')
    def index(self):
        return dict()
