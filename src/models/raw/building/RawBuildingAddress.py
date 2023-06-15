import shapely
from shapely import wkb
from shapely.geometry import shape


class RawBuildingAddress:
    id: int
    longitude: float
    latitude: float
    street: str
    housenumber: str
    postcode: float
    city: str
    geometry: shapely.Polygon

    def __init__(self, x, y, street, number, code, city, geometry):
        self.longitude = x
        self.latitude = y
        self.street = street
        self.housenumber = number
        self.postcode = code
        self.city = city
        self.geometry = shape(geometry)


class RawBuildingAddressDB(RawBuildingAddress):
    def __init__(self, *args):
        args = args[0]

        super().__init__(
            args[1],
            args[2],
            args[3],
            args[4],
            args[5],
            args[6],
            wkb.loads(args[7], hex=True).__geo_interface__
        )
        self.id = args[0]
