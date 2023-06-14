from _decimal import Decimal
from pandas import merge_asof, DataFrame

from models.data.BuildingData import BuildingDataRaw, BuildingDataDB


def filter_buildings(list):
    return list[(list['type'] == 'Residential') |
                (list['type'] == 'Apartments') |
                (list['type'] == 'Commerce') |
                (list['type'].str.startswith('Fire Department'))]


class BuildingRepository:
    def __init__(self, data_base_service):
        self.dbs = data_base_service
        self.building_data = []

    def initializeDB(self):
        [self.building_data.append(
            BuildingDataDB([float(x) if isinstance(x, Decimal) else x for x in row])) for row in
            self.dbs.select_all_from('building')]

    def initialize(self, raw_data):
        tmp_building_data: DataFrame = DataFrame()

        for col in raw_data:
            if len(tmp_building_data) == 0:
                tmp_building_data = raw_data[col]
            else:
                tmp_building_data = (
                    merge_asof(tmp_building_data.sort_values('coordinateX'), raw_data[col].sort_values('coordinateX'),
                               on='coordinateX', direction='nearest', tolerance=0.000009, suffixes=('', '_'))
                )

        tmp_building_data = filter_buildings(tmp_building_data)
        [self.building_data.append(BuildingDataRaw(row)) for row in tmp_building_data.itertuples()]

    def deleteAll(self):
        self.dbs.delete_all_from('building')

    def persist(self):
        self.dbs.write_data_to_database('building', self.building_data[0].__dict__, self.building_data)
