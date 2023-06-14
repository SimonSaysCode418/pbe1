import math

from models.data.PipePathData import PipePathData
from models.data.PipePointData import PipePointData
from models.data.ShortestPathConnector import ShortestPathConnector
from services.data.BuildingService import BuildingService
from services.data.PipeService import PipeService
from services.helper.BasicParameterService import BasicParameterService
from services.helper.Graph import find_shortest_paths, find_critical_path
from services.helper.PipeTypeService import PipeTypeService

class PipeCalculationService:
    def __init__(self, parameter_service, pipe_service, building_service):
        self.bps: BasicParameterService = parameter_service
        self.ps: PipeService = pipe_service
        self.bs: BuildingService = building_service

        self.pts: PipeTypeService = PipeTypeService(self.bps)

        self.pipe_points: list[PipePointData] = self.ps.get_pipe_point_data()
        self.pipe_paths: list[PipePathData] = self.ps.get_pipe_path_data()

        self.shortest_paths = None
        self.critical_path = None

    def __del__(self):
        del self.pts

    def run(self):
        self.set_building_data_to_connectors()

        start_point = next((point for point in self.pipe_points if point.type == 'Source'), None)
        self.shortest_paths = find_shortest_paths(start_point, self.pipe_points, self.pipe_paths)
        self.critical_path = find_critical_path(self.shortest_paths)

        self.pipe_paths = [path for path in self.pipe_paths if
                           any(path.id in short_path['path'] for short_path in self.shortest_paths)]

        self.initialize_paths()
        self.save_pipes()

    def initialize_paths(self):
        for path in self.pipe_paths:
            connectors = [short_path for short_path in self.shortest_paths if path.id in short_path['path']]

            path.massFlowRate = sum([point.massFlowRate for point in self.pipe_points if
                                     any(connector['connector'] == point.id for connector in connectors)])

            path.initialPipeDiameterFlow = self.calculate_initial_pipe_diameter(path, 'flow')
            path.initialPipeDiameterReturn = self.calculate_initial_pipe_diameter(path, 'return')

            [path.initialPipeTypeFlow,
             path.initialPipeNominalSizeFlow,
             path.initialPipeInsulationFlow,
             path.pipeDiameterFlow] = self.pts.get_pipe_element(path.initialPipeDiameterFlow)

            [path.initialPipeTypeReturn,
             path.initialPipeNominalSizeReturn,
             path.initialPipeInsulationReturn,
             path.pipeDiameterReturn] = self.pts.get_pipe_element(path.initialPipeDiameterReturn)

            path.pipeTypeFlow = path.initialPipeTypeFlow
            path.pipeNominalSizeFlow = path.initialPipeNominalSizeFlow
            path.pipeInsulationFlow = path.initialPipeInsulationFlow

            path.pipeTypeReturn = path.initialPipeTypeReturn
            path.pipeNominalSizeReturn = path.initialPipeNominalSizeReturn
            path.pipeInsulationReturn = path.initialPipeInsulationReturn

            self.optimize_pipe_by_pressure_loss(path)
            self.calculate_heat_loss(path)

    def optimize_pipe_by_pressure_loss(self, path):

        tolerable_pressure_loss = self.bps.get_parameter_value('Netzauslegung',
                                                               'tolerabler Druckverlust allgemein (Pa/m)')

        for index in range(10):
            # Ändern der Rohrdurchmesser, ab der 2. Iteration (1. Iteration = Initialisierung)
            if index > 0:
                change_flow = path.pipeSpecificPressureLossFlow > tolerable_pressure_loss
                change_return = path.pipeSpecificPressureLossReturn > tolerable_pressure_loss

                if not (change_flow | change_return):
                    return

                if change_flow:
                    [path.pipeTypeFlow,
                     path.pipeNominalSizeFlow,
                     path.pipeInsulationFlow,
                     path.pipeDiameterFlow] = self.pts.get_pipe_element_next_size(path.pipeTypeFlow,
                                                                                    path.pipeNominalSizeFlow)
                if change_return:
                    [path.pipeTypeReturn,
                     path.pipeNominalSizeReturn,
                     path.pipeInsulationReturn,
                     path.pipeDiameterReturn] = self.pts.get_pipe_element_next_size(path.pipeTypeReturn,
                                                                                      path.pipeNominalSizeReturn)

            # Wenn das Vorlaufrohr vom Typ ..-Duo ist, dann muss das Rücklaufrohr vom selben Typ sein
            if path.pipeTypeFlow.find('Duo'):
                path.pipeTypeReturn = path.pipeTypeFlow
                path.pipeNominalSizeReturn = path.pipeNominalSizeFlow
                path.pipeDiameterReturn = path.pipeDiameterFlow
                path.pipeInsulationReturn = path.pipeInsulationFlow

            # Vorlauf Berechnung
            path.pipeFlowVelocityFlow = self.calculate_flow_velocity(path.massFlowRate, path.pipeTypeFlow,
                                                                     path.pipeNominalSizeFlow, 'flow')
            path.pipeReynoldFlow = self.calculate_reynold(path.pipeFlowVelocityFlow, path.pipeDiameterFlow, 'flow')
            path.pipeLambdaFlow = self.calculate_lambda(path.pipeDiameterFlow, path.pipeReynoldFlow)
            path.pipePressureLossFlow = self.calculate_pressure_loss(path.pipeLambdaFlow, path.length,
                                                                     path.pipeDiameterFlow,
                                                                     path.pipeFlowVelocityFlow, 'flow')
            path.pipeSpecificPressureLossFlow = path.pipePressureLossFlow / path.length

            # Rücklauf Berechnung
            path.pipeFlowVelocityReturn = self.calculate_flow_velocity(path.massFlowRate, path.pipeTypeReturn,
                                                                       path.pipeNominalSizeReturn, 'return')
            path.pipeReynoldReturn = self.calculate_reynold(path.pipeFlowVelocityReturn, path.pipeDiameterReturn,
                                                            'return')
            path.pipeLambdaReturn = self.calculate_lambda(path.pipeDiameterReturn, path.pipeReynoldReturn)
            path.pipePressureLossReturn = self.calculate_pressure_loss(path.pipeLambdaReturn, path.length,
                                                                       path.pipeDiameterReturn,
                                                                       path.pipeFlowVelocityReturn, 'return')
            path.pipeSpecificPressureLossReturn = path.pipePressureLossReturn / path.length

    def set_building_data_to_connectors(self):
        for point in filter(lambda p: p.type == 'Connector', self.pipe_points):
            building = self.bs.get_building_by_point_geometry(point.geometry)
            point.powerHeatingW = building.powerHeating
            point.powerHotWaterW = building.powerHotWater

            heat_capacity = self.bps.get_parameter_value('Massenstrom', 'spez. Wärmekapazität Massenstrom (Ws/kgK)')
            temperature_delta = self.bps.get_parameter_value('Netzauslegung', 'Temperaturdelta Vor-Rücklauf (K)')

            point.massFlowRate = building.powerHeating / (heat_capacity * temperature_delta)

    def calculate_initial_pipe_diameter(self, path: PipePathData, flow_return):
        water_density = self.get_water_density(flow_return)
        initial_flow_velocity = self.bps.get_parameter_value('Netzauslegung_initial', 'Strömungsgeschwindigkeit (m/s)')

        return math.sqrt(
            4 * path.massFlowRate / (math.pi * initial_flow_velocity * water_density)) * 1000

    def calculate_flow_velocity(self, mass_flow_rate, pipe_type, pipe_nominal_size, flow_return):
        water_density = self.get_water_density(flow_return)
        inner_diameter = self.pts.get_inner_diameter(pipe_type, pipe_nominal_size)

        return (4.0 * mass_flow_rate) / (math.pi * water_density * (inner_diameter / 1000) ** 2)

    def get_water_density(self, flow_return):
        if flow_return == 'flow':
            return self.bps.get_parameter_value('Netzauslegung_initial', 'Dichte Wasser Vorlauf (kg/m³)')
        else:
            return self.bps.get_parameter_value('Netzauslegung_initial', 'Dichte Wasser Rücklauf (kg/m³)')

    def calculate_reynold(self, pipe_flow_velocity, pipe_inner_diameter, flow_return):
        if flow_return == 'flow':
            kinematic_viscosity = self.bps.get_parameter_value('Netzauslegung_initial',
                                                               'Kinematische Viskosität Vorlauf (m²/s)')
        else:
            kinematic_viscosity = self.bps.get_parameter_value('Netzauslegung_initial',
                                                               'Kinematische Viskosität Rücklauf (m²/s)')

        return (pipe_flow_velocity * (pipe_inner_diameter / 1000)) / kinematic_viscosity

    def calculate_lambda(self, pipe_inner_diameter, pipe_reynold) -> float:
        pipe_roughness = self.bps.get_parameter_value('Rohrauswahl', 'Rohrrauheit k (mm)')

        if self.pts.get_minimum_hydraulically_smooth() < pipe_reynold < self.pts.get_limit_hydraulically_smooth(
                pipe_inner_diameter):
            return 0.309 / ((math.log(pipe_reynold / 7)) ** 2)
        elif self.pts.get_limit_hydraulically_smooth(
                pipe_inner_diameter) < pipe_reynold < self.pts.get_limit_transitional_area(pipe_inner_diameter):
            return 0.25 / ((math.log(15.0 / pipe_reynold + pipe_roughness / (3.715 * pipe_inner_diameter))) ** 2)
        elif pipe_reynold > self.pts.get_limit_transitional_area(pipe_inner_diameter):
            return 0.25 / ((math.log((3.715 * pipe_inner_diameter) / pipe_roughness)) ** 2)
        return 64 / pipe_reynold

    def calculate_pressure_loss(self, pipe_lambda, pipe_length, pipe_diameter, pipe_flow_velocity, flow_return):
        water_density = self.get_water_density(flow_return)

        return pipe_lambda * (pipe_length / (pipe_diameter / 1000.0)) * water_density * (
                (pipe_flow_velocity ** 2) / 2.0)

    def calculate_heat_loss(self, path):
        # Wärmeverlust
        path.pipeHeatLossWinter = self.calculate_single_heat_loss(path.length,
                                                                  path.pipeTypeFlow, path.pipeTypeReturn,
                                                                  path.pipeNominalSizeFlow, path.pipeNominalSizeReturn,
                                                                  path.pipeInsulationFlow, path.pipeInsulationReturn,
                                                                  'winter')
        path.pipeHeatLossSummer = self.calculate_single_heat_loss(path.length,
                                                                  path.pipeTypeFlow, path.pipeTypeReturn,
                                                                  path.pipeNominalSizeFlow, path.pipeNominalSizeReturn,
                                                                  path.pipeInsulationFlow, path.pipeInsulationReturn,
                                                                  'summer')

        path.pipeSpecificHeatLossWinter = path.pipeHeatLossWinter / path.length
        path.pipeSpecificHeatLossSummer = path.pipeHeatLossSummer / path.length

        # Massenstrom anpassen

    def calculate_single_heat_loss(self, pipe_length, pipe_type_flow, pipe_type_return, pipe_nominal_size_flow,
                                   pipe_nominal_size_return,
                                   pipe_insulation_flow, pipe_insulation_return, winter_summer):

        if winter_summer == 'winter':
            floor_temperature = self.bps.get_parameter_value('Netzauslegung', 'Bodentemperatur Winter (K)')
        else:
            floor_temperature = self.bps.get_parameter_value('Netzauslegung', 'Bodentemperatur Sommer (K)')

        water_temperature_flow = self.bps.get_parameter_value('Netzauslegung', 'Vorlauftemperatur (K)')
        water_temperature_return = self.bps.get_parameter_value('Netzauslegung', 'Rücklauftemperatur (K)')

        specific_heat_loss_flow = self.pts.get_heat_loss(pipe_type_flow, pipe_nominal_size_flow, pipe_insulation_flow)
        specific_heat_loss_return = self.pts.get_heat_loss(pipe_type_return, pipe_nominal_size_return,
                                                           pipe_insulation_return)

        return ((specific_heat_loss_flow + specific_heat_loss_return) / 2.0) * (
                0.5 * (water_temperature_flow + water_temperature_return) - floor_temperature) * pipe_length

    def save_pipes(self):
        shortest_path_objects = []
        for short_path in self.shortest_paths:
            for path_id in short_path['path']:
                shortest_path_objects.append(ShortestPathConnector(short_path['connector'], path_id))

        self.ps.set_pipe_point_data(self.pipe_points)
        self.ps.set_pipe_path_data(self.pipe_paths)
        self.ps.set_shortest_path_connector_data(shortest_path_objects)
