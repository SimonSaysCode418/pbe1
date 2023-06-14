from shapely import wkb
from shapely.geometry import shape


class PipePathData(object):
    def __init__(self):
        self.id = 0
        self.startPointId = 0
        self.endPointId = 0
        self.length = 0
        self.geometry = ''

        self.massFlowRate = 0

        self.initialPipeDiameterFlow = 0
        self.initialPipeTypeFlow = ''
        self.initialPipeNominalSizeFlow = 0
        self.initialPipeInsulationFlow = ''

        self.initialPipeDiameterReturn = 0
        self.initialPipeTypeReturn = ''
        self.initialPipeNominalSizeReturn = 0
        self.initialPipeInsulationReturn = ''

        self.pipeTypeFlow = ''
        self.pipeNominalSizeFlow = 0
        self.pipeInsulationFlow = ''
        self.pipeDiameterFlow = 0
        self.pipeFlowVelocityFlow = 0
        self.pipeReynoldFlow = 0
        self.pipeLambdaFlow = 0
        self.pipePressureLossFlow = 0
        self.pipeSpecificPressureLossFlow = 0

        self.pipeTypeReturn = ''
        self.pipeNominalSizeReturn = 0
        self.pipeInsulationReturn = ''
        self.pipeDiameterReturn = 0
        self.pipeFlowVelocityReturn = 0
        self.pipeReynoldReturn = 0
        self.pipeLambdaReturn = 0
        self.pipePressureLossReturn = 0
        self.pipeSpecificPressureLossReturn = 0

        self.pipeHeatLossWinter = 0
        self.pipeSpecificHeatLossWinter = 0
        self.pipeHeatLossSummer = 0
        self.pipeSpecificHeatLossSummer = 0



class PipePathDataRaw(PipePathData):
    def __init__(self, args):
        super().__init__()

        self.id = getattr(args, 'id')
        self.startPointId = getattr(args, 'startPointId')
        self.endPointId = getattr(args, 'endPointId')
        self.length = getattr(args, 'length')
        self.geometry = shape(getattr(args, 'geometry'))


class PipePathDataDB(PipePathData):
    def __init__(self, args):
        super().__init__()

        self.id = args[0]
        self.startPointId = args[1]
        self.endpointId = args[2]
        self.length = args[3]
        self.geometry = shape(wkb.loads(args[5], hex=True).__geo_interface__)