import sys
from services.calculations.BuildingCalculationService import BuildingCalculationService
from services.calculations.PipeCalculationService import PipeCalculationService
from services.data.BuildingService import BuildingService
from services.data.PipeService import PipeService
from services.helper.BasicParameterService import BasicParameterService
from services.data.RawDataService import RawDataService


def main():
    raw_data_service = RawDataService()

    user_input = input('Rohdaten-Tabellen neu anlegen und Daten einlesen? (y/n): ')
    if user_input.lower() == 'y':
        raw_data_service.import_data()
    else:
        raw_data_service.initializeDB()

    parameter_service = BasicParameterService()
    building_service = BuildingService()

    user_input = input('Gebäudedaten neu berechnen? (y/n): ')
    if user_input.lower() == 'y':
        building_service.initialize(raw_data_service)
        building_calculation = BuildingCalculationService(parameter_service, building_service)
        building_calculation.run()

        del building_calculation
    else:
        building_service.initializeDB()

    pipe_service = PipeService()

    user_input = input('Rohrdaten neu berechnen? (y/n): ')
    if user_input.lower() == 'y':
        pipe_service.initialize(raw_data_service)
        pipe_calculation = PipeCalculationService(parameter_service, pipe_service, building_service)
        pipe_calculation.run()

        del pipe_calculation
    else:
        pipe_service.initializeDB()

    del raw_data_service
    del building_service
    del pipe_service


if __name__ == "__main__":
    main()
    sys.exit()
