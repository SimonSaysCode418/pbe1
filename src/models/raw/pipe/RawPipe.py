import shapely
from shapely import wkb
from shapely.geometry import shape


class RawPipe:
    id: int
    startRawPointId: int
    endRawPointId: int
    length: float
    geometry: shapely.LineString

    def __init__(self, length, geometry):
        self.length = length
        self.geometry = shape(geometry)


class RawPipeDB(RawPipe):
    def __init__(self, *args):
        args = args[0]

        super().__init__(
            args[3],
            wkb.loads(args[4], hex=True).__geo_interface__
        )
        self.id = args[0]
        self.startRawPointId = args[1]
        self.endRawPointId = args[2]
