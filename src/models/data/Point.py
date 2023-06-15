import shapely
from shapely import wkb
from shapely.geometry import shape


class Point(object):
    id: int
    type: str
    powerHeating: float
    powerHotWater: float
    massFlowRate: float
    geometry: shapely.Point

    def __init__(self, *args):
        self.powerHeating = 0
        self.powerHotWater = 0
        self.massFlowRate = 0
        if len(args):
            args = args[0]
            self.id = getattr(args, 'id')
            self.type = getattr(args, 'type')
            self.geometry = shape(getattr(args, 'geometry'))


class PointDB(Point):
    def __init__(self, *args):
        super().__init__()

        self.id = args[0]
        self.type = args[1]
        self.name = args[2]
        self.geometry = shape(wkb.loads(args[3], hex=True).__geo_interface__)
