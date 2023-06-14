from shapely import wkb


class RawPipePoint:
    def __init__(self, point_type, geometry):
        self.id = 0
        self.type = point_type
        self.name = ''
        self.geometry = geometry

class RawPipePointDB(RawPipePoint):
    def __init__(self, *args):
        args = args[0]

        super().__init__(
            args[1],
            wkb.loads(args[3], hex=True).__geo_interface__,
        )
        self.id = args[0]
        self.name = args[2]
