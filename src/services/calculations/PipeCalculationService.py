import math

from models.data.Pipe import Pipe
from models.data.Point import Point
from models.data.ShortestPathConnector import ShortestPathConnector
from services.data.BuildingService import BuildingService
from services.data.PipeService import PipeService
from services.helper.BasicParameterService import BasicParameterService
from services.helper.Graph import find_shortest_paths, find_critical_path
from services.helper.PipeTypeService import PipeTypeService

translator = {
    "Flow": "Vorlauf",
    "Return": "Rücklauf"
}


class PipeCalculationService:
    def __init__(self, parameter_service, pipe_service, building_service):
        self.bps: BasicParameterService = parameter_service
        self.ps: PipeService = pipe_service
        self.bs: BuildingService = building_service

        self.pts: PipeTypeService = PipeTypeService(self.bps)

        self.points: list[Point] = self.ps.get_point_data()
        self.pipes: list[Pipe] = self.ps.get_pipe_data()
        self.connector_pipes = list[Pipe]

        self.shortest_paths = None
        self.critical_path = None

    def __del__(self):
        del self.pts

    def run(self):
        self.set_building_data_to_connectors()

        start_point = next((point for point in self.points if point.type == 'Source'), None)
        self.shortest_paths = find_shortest_paths(start_point, self.points, self.pipes)
        self.critical_path = find_critical_path(self.shortest_paths)

        self.pipes = [pipe for pipe in self.pipes if
                      any(pipe.id in short_path['path'] for short_path in self.shortest_paths)]

        for pipe in self.pipes:
            if any(point.type == 'Connector' for point in self.points if
                   point.id == pipe.startPointId or point.id == pipe.endPointId):
                pipe.location = "Connector"
            else:
                pipe.location = "Path"

            pipe.initialMassFlowRate = self.calculate_mass_flow_rate(pipe)
            pipe.massFlowRate = pipe.initialMassFlowRate
            self.initialize_pipe(pipe, 'Flow')
            self.initialize_pipe(pipe, 'Return')
            self.calculate_pressure_loss(pipe, 'Flow')
            self.calculate_pressure_loss(pipe, 'Return')

        share_network_heat_loss = 0
        building_energy_demand = sum(
            [building.demandHeating + building.demandHotWater for building in self.bs.get_building_data()])

        while True:
            last_iteration_share_network_heat_loss = share_network_heat_loss

            network_power_heat_loss = 0
            for pipe in self.pipes:
                pipe.massFlowRate = pipe.initialMassFlowRate * (1 + share_network_heat_loss)
                self.optimize_pipe_by_pressure_loss(pipe)

                pipe.heatLossWinter = self.calculate_heat_loss(pipe, 'Winter')
                pipe.heatLossSummer = self.calculate_heat_loss(pipe, 'Sommer')
                network_power_heat_loss += (pipe.heatLossWinter / pipe.heatLossSummer) / 2

                pipe.costsFlow = round(pipe.specificCostsFlow * pipe.length, 2)
                pipe.costsReturn = round(pipe.specificCostsReturn * pipe.length, 2)

            share_network_heat_loss = (network_power_heat_loss * 8760) / building_energy_demand

            # TODO: delta < 2 statt delta = 0 (2 statt 3 Iterationen)
            if (share_network_heat_loss - last_iteration_share_network_heat_loss) < 0.02:
                break

        self.save_pipes()

    def set_building_data_to_connectors(self):
        for point in filter(lambda p: p.type == 'Connector', self.points):
            building = self.bs.get_building_by_point_geometry(point.geometry)
            point.powerHeating = building.powerHeating
            point.powerHotWater = building.powerHotWater

            heat_capacity = self.bps.get_parameter_value('Netzauslegung', 'spez. Wärmekapazität Massenstrom (Ws/kgK)')
            water_temperature_flow = self.bps.get_parameter_value('Netzauslegung', 'Vorlauftemperatur Winter (K)')
            water_temperature_return = self.bps.get_parameter_value('Netzauslegung', 'Rücklauftemperatur Winter (K)')

            point.massFlowRate = building.powerHeating / (
                    heat_capacity * (water_temperature_flow - water_temperature_return))

    def calculate_mass_flow_rate(self, pipe):
        connectors = [short_path for short_path in self.shortest_paths if pipe.id in short_path['path']]

        return sum([point.massFlowRate for point in self.points if
                    any(connector['connector'] == point.id for connector in connectors)])

    def initialize_pipe(self, pipe, flow_return):
        initial_diameter = self.calculate_initial_pipe_diameter(pipe, flow_return)

        [initial_type,
         initial_nominal_size,
         initial_insulation,
         diameter, specific_costs] = self.pts.get_pipe_element(initial_diameter)

        setattr(pipe, 'initialType' + flow_return, initial_type)
        setattr(pipe, 'initialNominalSize' + flow_return, initial_nominal_size)
        setattr(pipe, 'initialDiameter' + flow_return, initial_diameter)
        setattr(pipe, 'initialInsulation' + flow_return, initial_insulation)

        setattr(pipe, 'type' + flow_return, initial_type)
        setattr(pipe, 'nominalSize' + flow_return, initial_nominal_size)
        setattr(pipe, 'diameter' + flow_return, diameter)
        setattr(pipe, 'insulation' + flow_return, initial_insulation)
        setattr(pipe, 'specificCosts' + flow_return, specific_costs)

    def calculate_initial_pipe_diameter(self, path, flow_return):
        water_density = self.get_water_density(flow_return)
        initial_flow_velocity = self.bps.get_parameter_value('Netzauslegung', 'Strömungsgeschwindigkeit (m/s)')
        return math.sqrt(
            4 * path.initialMassFlowRate / (math.pi * initial_flow_velocity * water_density)) * 1000

    def optimize_pipe_by_pressure_loss(self, pipe):
        tolerable_pressure_loss = self.bps.get_parameter_value('Netzauslegung',
                                                               'tolerabler Druckverlust allgemein (Pa/m)')
        for index in range(10):
            change_flow = pipe.specificPressureLossFlow > tolerable_pressure_loss
            change_return = pipe.specificPressureLossReturn > tolerable_pressure_loss

            if not (change_flow | change_return):
                return

            if change_flow:
                [pipe.typeFlow,
                 pipe.nominalSizeFlow,
                 pipe.insulationFlow,
                 pipe.diameterFlow,
                 pipe.specificCostsFlow] = self.pts.get_pipe_element_next_size(pipe.typeFlow,
                                                                               pipe.nominalSizeFlow)
            if change_return:
                [pipe.typeReturn,
                 pipe.nominalSizeReturn,
                 pipe.insulationReturn,
                 pipe.diameterReturn,
                 pipe.specificCostsReturn] = self.pts.get_pipe_element_next_size(pipe.typeReturn,
                                                                                 pipe.nominalSizeReturn)

            # Wenn das Vorlaufrohr vom Typ ..-Duo ist, dann muss das Rücklaufrohr vom selben Typ sein
            if pipe.typeFlow.find('Duo'):
                self.set_duo_pipe_type(pipe)

            self.calculate_pressure_loss(pipe, 'Flow')
            self.calculate_pressure_loss(pipe, 'Return')

    def set_duo_pipe_type(self, pipe):
        pipe.typeReturn = pipe.typeFlow
        pipe.nominalSizeReturn = pipe.nominalSizeFlow
        pipe.diameterReturn = pipe.diameterFlow
        pipe.insulationReturn = pipe.insulationFlow

    def calculate_pressure_loss(self, pipe, flow_return):
        mass_flow_rate = getattr(pipe, 'massFlowRate')
        inner_diameter = getattr(pipe, 'diameter' + flow_return)

        flow_velocity = self.calculate_flow_velocity(mass_flow_rate, inner_diameter, flow_return)
        reynold = self.calculate_reynold(flow_velocity, inner_diameter, flow_return)
        _lambda = self.calculate_lambda(inner_diameter, reynold)

        water_density = self.get_water_density(flow_return)
        pressure_loss = _lambda * (pipe.length / (inner_diameter / 1000.0)) * water_density * (
                (flow_velocity ** 2) / 2.0)

        pressure_loss = pressure_loss * (
                    1 + self.bps.get_parameter_value('Netzauslegung', 'Anteil Druckverlust Einbauteile'))

        specific_pressure_loss = pressure_loss / pipe.length

        setattr(pipe, 'flowVelocity' + flow_return, flow_velocity)
        setattr(pipe, 'reynold' + flow_return, reynold)
        setattr(pipe, 'lambda' + flow_return, _lambda)
        setattr(pipe, 'pressureLoss' + flow_return, pressure_loss)
        setattr(pipe, 'specificPressureLoss' + flow_return, specific_pressure_loss)

    def calculate_flow_velocity(self, mass_flow_rate, inner_diameter, flow_return):
        water_density = self.get_water_density(flow_return)
        return (4.0 * mass_flow_rate) / (math.pi * water_density * (inner_diameter / 1000) ** 2)

    def get_water_density(self, flow_return):
        return self.bps.get_parameter_value('Netzauslegung', 'Dichte Wasser ' +
                                            translator[flow_return] + ' (kg/m³)')

    def calculate_reynold(self, pipe_flow_velocity, inner_diameter, flow_return):
        kinematic_viscosity = self.bps.get_parameter_value('Netzauslegung',
                                                           'Kinematische Viskosität ' +
                                                           translator[flow_return] + ' (m²/s)')
        return (pipe_flow_velocity * (inner_diameter / 1000)) / kinematic_viscosity

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

    def calculate_heat_loss(self, pipe, winter_summer):
        floor_temperature = self.bps.get_parameter_value('Netzauslegung', 'Bodentemperatur ' + winter_summer + ' (K)')
        water_temperature_flow = self.bps.get_parameter_value('Netzauslegung',
                                                              'Vorlauftemperatur ' + winter_summer + ' (K)')
        water_temperature_return = self.bps.get_parameter_value('Netzauslegung',
                                                                'Rücklauftemperatur ' + winter_summer + ' (K)')

        specific_heat_loss_flow = self.pts.get_heat_loss(pipe.typeFlow, pipe.nominalSizeFlow, pipe.insulationFlow)
        specific_heat_loss_return = self.pts.get_heat_loss(pipe.typeReturn, pipe.nominalSizeReturn,
                                                           pipe.insulationReturn)

        return ((specific_heat_loss_flow + specific_heat_loss_return) / 2.0) * (
                0.5 * (water_temperature_flow + water_temperature_return) - floor_temperature) * pipe.length

    def save_pipes(self):
        shortest_path_objects = []
        for sp_object in self.shortest_paths:
            for path_id in sp_object['path']:
                shortest_path_objects.append(ShortestPathConnector(sp_object['connector'], path_id))

        self.ps.set_point_data(self.points)
        self.ps.set_pipe_data(self.pipes)
        self.ps.set_shortest_path_connector_data(shortest_path_objects)
