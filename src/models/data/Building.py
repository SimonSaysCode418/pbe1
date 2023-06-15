import shapely
from shapely import wkb
from shapely.geometry import shape


class Building(object):
    id: int
    street: str
    housenumber: str
    postcode: float
    city: str
    type: str
    floorArea: float
    wallAreaPerFloor: float
    roof: str
    groupname: str
    yearOfConstruction: float
    floors: float
    wallArea: float
    roofArea: float
    surface: float
    energyReferenceArea: float
    livingArea: float
    volumeLivingArea: float
    transmissionSurface: float
    transmission: float
    ventilationHeatLoss: float
    ventilationHeatLossComplex: float
    powerHotWater: float
    powerHeating: float
    demandHotWater: float
    demandHeating: float
    fullLoadHours: float
    geometry: shapely.Polygon

    def __init__(self, *args):
        if len(args):
            args = args[0]
            if not isinstance(args, list):
                self.street = getattr(args, 'street')
                self.housenumber = getattr(args, 'housenumber')
                self.postcode = getattr(args, 'postcode')
                self.city = getattr(args, 'city')
                self.type = getattr(args, 'type')
                self.floorArea = getattr(args, 'floorArea')
                self.wallAreaPerFloor = getattr(args, 'wallArea')
                self.roof = getattr(args, 'roof')
                self.geometry = shape(getattr(args, 'geometry'))
            else:
                for index, attribute in enumerate(self.__annotations__.keys()):
                    if attribute != "geometry":
                        setattr(self, attribute, args[index])
                    else:
                        setattr(self, attribute, shape(wkb.loads(args[index], hex=True).__geo_interface__))
