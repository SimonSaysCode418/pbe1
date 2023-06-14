import json
from shapely import wkb
from shapely.geometry import shape


class RawBuildingHeight:
    def __init__(self, x, y, height, roof_shape, geometry):
        self.coordinateX = x
        self.coordinateY = y
        self.height = height
        self.roof = roof_shape
        self.geometry = shape(geometry)


class RawBuildingHeightDB(RawBuildingHeight):
    def __init__(self, *args):
        args = args[0]

        super().__init__(
            args[1],
            args[2],
            args[3],
            args[4],
            wkb.loads(args[5], hex=True).__geo_interface__
        )
        self.id = args[0]
