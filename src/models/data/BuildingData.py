from shapely.geometry import shape


class BuildingData(object):
    def __init__(self):
        self.street = ''
        self.housenumber = ''
        self.postcode = 0
        self.city = ''
        self.type = ''
        self.groundArea = 0
        self.wallAreaPerFloor = 0
        self.roof = ''
        self.geometry = ''

        self.groupname = ''
        self.yearOfConstruction = ''
        self.floors = 0
        self.wallArea = 0
        self.roofArea = 0
        self.surface = 0
        self.energyReferenceArea = 0
        self.livingArea = 0
        self.volumeLivingArea = 0
        self.transmissionSurface = 0
        self.transmission = 0
        self.ventilationHeatLoss = 0
        self.ventilationHeatLossComplex = 0
        self.powerHotWater = 0
        self.powerHeating = 0
        self.demandHotWater = 0
        self.demandHeating = 0
        self.fullLoadHours = 0


class BuildingDataRaw(BuildingData):
    def __init__(self, args):
        super().__init__()

        self.street = getattr(args, 'street')
        self.housenumber = getattr(args, 'housenumber')
        self.postcode = getattr(args, 'postcode')
        self.city = getattr(args, 'city')
        self.type = getattr(args, 'type')
        self.groundArea = getattr(args, 'groundArea')
        self.wallAreaPerFloor = getattr(args, 'wallArea')
        self.roof = getattr(args, 'roof')
        self.geometry = shape(getattr(args, 'geometry'))


class BuildingDataDB(BuildingData):
    def __init__(self, args):
        super().__init__()

        for index, attribute in enumerate(self.__dict__.keys()):
            index += 1
            print(attribute)
            # print(attribute != "geometry")
            # if attribute != "geometry":
            #     setattr(self, attribute, args[index])
            # else:
            #     setattr(self, attribute, shape(wkb.loads(args[index], hex=True).__geo_interface__))

        # self.street = args[1]
        # self.housenumber = args[2]
        # self.postcode = args[3]
        # self.city = args[4]
        # self.type = args[5]
        # self.yearOfConstruction = args[6]
        # self.groupname = args[7]
        # self.roof = args[8]
        # self.floors = args[9]
        # self.groundArea = args[10]
        # self.energyReferenceArea = args[11]
        # self.livingArea = args[12]
        # self.wallAreaPerFloor = args[13]
        # self.wallArea = args[14]
        # self.roofArea = args[15]
        # self.surface = args[16]
        # self.volumeLivingArea = args[17]
        # self.transmissionSurface = args[18]
        # self.transmission = args[19]
        # self.ventilationHeatLoss = args[20]
        # self.ventilationHeatLossComplex = args[21]
        # self.powerHeating = args[22]
        # self.powerHotWater = args[23]
        # self.demandHeating = args[24]
        # self.demandHotWater = args[25]
        # self.fullLoadHours = args[26]
        # self.geometry = shape(wkb.loads(args[27], hex=True).__geo_interface__)
