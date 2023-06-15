from services.database.DataBaseService import DataBaseService
from models.data.Building import Building
from repositories.BuildingRepository import BuildingRepository


class BuildingService:
    def __init__(self):
        self.dbs = DataBaseService()
        self.br = BuildingRepository(self.dbs)

    def __del__(self):
        del self.dbs
        del self.br

    def initialize(self, raw_data_service):
        self.dbs.create_table_from_class(Building)
        self.br.initialize(raw_data_service.get_raw_building_data())

    def initializeDB(self):
        self.br.initializeDB()

    def get_building_data(self) -> list[Building]:
        return self.br.building_data

    def get_building_by_point_geometry(self, point_geometry):
        for data in self.get_building_data():
            if data.geometry.contains(point_geometry):
                return data
        return None

    def set_building_data(self, buildings):
        self.br.building_data = buildings
        self.br.persist()
