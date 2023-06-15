import shapely
from shapely import wkb
from shapely.geometry import shape


class RawBuildingThermosData(object):
    id: int
    type: str
    longitude: float
    latitude: float
    kwpCooling: float
    kwpDemand: float
    kwhCooling: float
    kwhDemand: float
    floorArea: float
    wallArea: float
    geometry: shapely.Polygon

    def __init__(self, building_type, x, y, kwp_c, kwp_d, kwh_c, kwh_d, ground_area, wall_area, geometry):
        self.type = building_type
        self.longitude = x
        self.latitude = y
        self.kwpCooling = kwp_c
        self.kwpDemand = kwp_d
        self.kwhCooling = kwh_c
        self.kwhDemand = kwh_d
        self.floorArea = ground_area
        self.wallArea = wall_area
        self.geometry = shape(geometry)


class RawBuildingThermosDataDB(RawBuildingThermosData):
    def __init__(self, *args):
        args = args[0]

        super().__init__(
            args[1],
            args[2],
            args[3],
            args[4],
            args[5],
            args[6],
            args[7],
            args[8],
            args[9],
            wkb.loads(args[10], hex=True).__geo_interface__
        )
        self.id = args[0]
