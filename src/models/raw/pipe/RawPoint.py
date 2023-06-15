import shapely
from shapely import wkb


class RawPoint:
    id: int
    type: str
    geometry: shapely.Point

    def __init__(self, point_type, geometry):
        self.type = point_type
        self.geometry = geometry


class RawPointDB(RawPoint):
    def __init__(self, *args):
        args = args[0]

        super().__init__(
            args[1],
            wkb.loads(args[2], hex=True).__geo_interface__,
        )
        self.id = args[0]
