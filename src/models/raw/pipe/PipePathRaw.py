from shapely import wkb
from shapely.geometry import shape


class RawPipePath:
    def __init__(self, length, geometry):
        self.id = 0
        self.startPointId = 0
        self.endPointId = 0
        self.length = length
        self.geometry = shape(geometry)


class RawPipePathDB(RawPipePath):
    def __init__(self, *args):
        args = args[0]

        super().__init__(
            args[3],
            wkb.loads(args[4], hex=True).__geo_interface__
        )
        self.id = args[0]
        self.startPointId = args[1]
        self.endPointId = args[2]
