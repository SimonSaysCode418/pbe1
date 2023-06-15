import shapely
from shapely import wkb
from shapely.geometry import shape


class RawBuildingHeight:
    id: int
    longitude: float
    latitude: float
    height: float
    roof: str
    geometry: shapely.Polygon

    def __init__(self, x, y, height, roof_shape, geometry):
        self.longitude = x
        self.latitude = y
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
