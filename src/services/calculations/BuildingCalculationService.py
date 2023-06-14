from services.helper.BuildingParameterService import BuildingParameterService
from services.data.BuildingService import BuildingService
from services.helper.IWUService import IWUService
from services.helper.BasicParameterService import BasicParameterService
from models.data.BuildingData import BuildingData


class BuildingCalculationService:
    def __init__(self, parameter_service, building_service):
        self.ps: BasicParameterService = parameter_service
        self.bs: BuildingService = building_service

        self.iwus: IWUService = IWUService()
        self.bps: BuildingParameterService = BuildingParameterService()

        self.building_data: list[BuildingData] = self.bs.get_building_data()

    def __del__(self):
        del self.iwus
        del self.bps
    def run(self):
        for building in self.building_data:
            building.yearOfConstruction = self.bps.get_year_of_construction(building)
            building.groupname = self.bps.get_building_group()
            building.floors = self.ps.get_parameter_value('Etagen', building.type)
            building.wallArea = building.floors * building.wallAreaPerFloor
            building.roofArea = building.groundArea / (
                self.ps.get_parameter_value('Gebäudefaktor', 'Giebeldachfläche') if building.roof == 'gabled' else 1)
            building.surface = building.wallArea + building.roofArea
            building.energyReferenceArea = building.groundArea * building.floors * self.ps.get_parameter_value(
                'Gebäudefaktor', 'Energiebezugsfläche')
            building.livingArea = building.energyReferenceArea * self.ps.get_parameter_value(
                'Gebäudefaktor', 'Wohnfläche')
            building.volumeLivingArea = building.livingArea * self.ps.get_parameter_value(
                'Gebäudefaktor', 'Raumhöhe (m)')
            building.transmissionSurface = self.calculateTransmissionSurface(building)
            building.transmission = self.calculateTransmissionLivingArea(building)
            building.ventilationHeatLoss = self.calculateVentilationHeatLoss(building, 0)
            building.ventilationHeatLossComplex = self.calculateVentilationHeatLoss(building, 1)
            building.powerHotWater = self.calculatePowerHotWaterW(building)
            building.powerHeating = building.transmission + building.ventilationHeatLoss
            building.demandHotWater = self.calculateDemandHotWaterWH(building)
            building.demandHeating = self.calculateDemandHeatingWH(building)
            building.fullLoadHours = (building.demandHeating + building.demandHotWater) / (
                    building.powerHeating + building.powerHotWater)

        self.save_buildings()
    def calculateTransmissionSurface(self, building):
        coefficient = self.iwus.get_iwu_value(building.type, building.yearOfConstruction,
                                              'Wärmetransferkoeffizient Hüllfläche (W/m²K)')
        temperature_in, temperature_out = self.get_temperature(building)
        transmission = coefficient * building.surface * (temperature_in - temperature_out)

        if (building.type.startswith('Fire Department')) | (building.type == 'Commerce'):
            transmission = transmission * self.ps.get_parameter_value('Transmissionswärmeverlust',
                                                                      'Geschäfts- und Feuerwehrtransmission')

        return transmission

    def calculateTransmissionLivingArea(self, building):
        coefficient = self.iwus.get_iwu_value(building.type, building.yearOfConstruction,
                                              'Wärmetransferkoeffizient Wohnfläche (W/m²K)')
        temperature_in, temperature_out = self.get_temperature(building)
        transmission = coefficient * building.livingArea * (temperature_in - temperature_out)

        if (building.type.startswith('Fire Department')) | (building.type == 'Commerce'):
            transmission = transmission * self.ps.get_parameter_value('Transmissionswärmeverlust',
                                                                      'Geschäfts- und Feuerwehrtransmission')

        return transmission

    def calculateVentilationHeatLoss(self, building, complex):
        air_exchange_rate = self.ps.get_parameter_value('Lüftungswechselwärmeverlust', 'Luftwechselzahl')
        heat_capacity_air = self.ps.get_parameter_value('Lüftungswechselwärmeverlust',
                                                        'spez. Wärmekapazität Luft (kJ/kgK)')
        air_density_in = self.ps.get_parameter_value('Lüftungswechselwärmeverlust', 'Luftdichte [21°C] (kg/m³)')
        air_density_out = self.ps.get_parameter_value('Lüftungswechselwärmeverlust', 'Luftdichte [-12°C] (kg/m³)')
        temperature_in, temperature_out = self.get_temperature(building)

        if complex:
            ventilation_heat_loss = abs(air_exchange_rate * building.volumeLivingArea * heat_capacity_air * (
                    air_density_in * temperature_in - air_density_out * temperature_out))
        else:
            ventilation_heat_loss = abs(air_exchange_rate * building.volumeLivingArea * heat_capacity_air * (
                    (air_density_in + air_density_out) / 2) * (temperature_in - temperature_out))
        return ventilation_heat_loss

    def calculatePowerHotWaterW(self, building):
        heat_production = self.iwus.get_iwu_value(building.type, building.yearOfConstruction,
                                                  'Wärmeerzeugung WW (kWh/m²a)')

        full_load_hours_hot_water = self.ps.get_parameter_value('Warmwasser', 'Volllaststunden')

        power_hot_water = building.livingArea * heat_production / full_load_hours_hot_water * 1000

        if building.type == 'Fire Department Administration':
            power_hot_water = power_hot_water * self.ps.get_parameter_value('Warmwasser',
                                                                            'Feuerwehrhauptgebäude')
        if (building.type.find('Seminar') > -1) | (building.type == 'Commerce'):
            power_hot_water = 0  # Kein Warmwasser in den Seminarräumen und beim Autohändler

        return power_hot_water

    def get_temperature(self, building):
        temperature_in = self.ps.get_parameter_value('Allgemein', 'Innentemperatur (K)')
        temperature_out = self.ps.get_parameter_value('Allgemein',
                                                      'Außentemperatur Seminarraumnutzung (K)') if building.type.find(
            'Seminar') > -1 else self.ps.get_parameter_value('Allgemein', 'Außentemperatur (K)')

        return temperature_in, temperature_out

    def calculateDemandHotWaterWH(self, building):
        demand_hot_water = building.livingArea * self.iwus.get_iwu_value(
            building.type, building.yearOfConstruction, 'Wärmeerzeugung WW (kWh/m²a)')

        if building.type == 'Fire Department Administration':
            demand_hot_water = demand_hot_water * self.ps.get_parameter_value('Warmwasser',
                                                                              'Feuerwehrhauptgebäude')
        if (building.type.find('Seminar') > -1) | (building.type == 'Commerce'):
            demand_hot_water = 0  # Kein Warmwasser in den Seminarräumen und beim Autohändler

        return demand_hot_water * 1000

    def calculateDemandHeatingWH(self, building):
        demand_heating = building.livingArea * self.iwus.get_iwu_value(
            building.type, building.yearOfConstruction, 'Wärmeerzeugung Heizung (kWh/m²a)')

        if building.type == 'Fire Department Administration':
            demand_heating = demand_heating * self.ps.get_parameter_value('Heizung',
                                                                          'Feuerwehrhauptgebäude')
        if building.type == 'Fire Department Seminar':
            demand_heating = demand_heating * self.ps.get_parameter_value('Heizung',
                                                                          'Feuerwehrseminarraum')
        if building.type == 'Commerce':
            demand_heating = demand_heating * self.ps.get_parameter_value('Heizung',
                                                                          'Geschäftsgebäude')

        return demand_heating * 1000

    def save_buildings(self):
        self.bs.set_building_data(self.building_data)
