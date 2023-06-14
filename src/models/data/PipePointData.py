from shapely import wkb
from shapely.geometry import shape


class PipePointData(object):
    def __init__(self):
        self.id = 0
        self.type = ''
        self.name = ''
        self.geometry = ''

        self.powerHeatingW = 0
        self.powerHotWaterW = 0
        self.massFlowRate = None


class PipePointDataRaw(PipePointData):
    def __init__(self, args):
        super().__init__()

        self.id = getattr(args, 'id')
        self.type = getattr(args, 'type')
        self.name = getattr(args, 'name')
        self.geometry = shape(getattr(args, 'geometry'))


class PipePointDataDB(PipePointData):
    def __init__(self, args):
        super().__init__()

        self.id = args[0]
        self.type = args[1]
        self.name = args[2]
        self.geometry = shape(wkb.loads(args[3], hex=True).__geo_interface__)
