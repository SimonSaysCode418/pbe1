import shapely
from shapely import wkb
from shapely.geometry import shape


class Pipe(object):
    id: int
    startPointId: float
    endPointId: float
    length: float
    geometry: shapely.LineString

    massFlowRate: float

    initialDiameterFlow: float
    initialTypeFlow: str
    initialNominalSizeFlow: float
    initialInsulationFlow: str

    initialDiameterReturn: float
    initialTypeReturn: str
    initialNominalSizeReturn: float
    initialInsulationReturn: str

    typeFlow: str
    nominalSizeFlow: float
    insulationFlow: str
    diameterFlow: float
    flowVelocityFlow: float
    reynoldFlow: float
    lambdaFlow: float
    pressureLossFlow: float
    specificPressureLossFlow: float

    typeReturn: str
    nominalSizeReturn: float
    insulationReturn: str
    diameterReturn: float
    flowVelocityReturn: float
    reynoldReturn: float
    lambdaReturn: float
    pressureLossReturn: float
    specificPressureLossReturn: float

    heatLossWinter: float
    specificHeatLossWinter: float
    heatLossSummer: float
    specificHeatLossSummer: float

    def __init__(self, *args):
        if len(args):
            args = args[0]
            self.id = getattr(args, 'id')
            self.startPointId = getattr(args, 'startRawPointId')
            self.endPointId = getattr(args, 'endRawPointId')
            self.length = getattr(args, 'length')
            self.geometry = shape(getattr(args, 'geometry'))


class PipeDB(Pipe):
    def __init__(self, *args):
        super().__init__()

        self.id = args[0]
        self.startPointId = args[1]
        self.endpointId = args[2]
        self.length = args[3]
        self.geometry = shape(wkb.loads(args[5], hex=True).__geo_interface__)
