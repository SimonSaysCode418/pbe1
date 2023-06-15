from _decimal import Decimal
from pandas import merge_asof, DataFrame

from models.data.Building import Building


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
            Building([float(x) if isinstance(x, Decimal) else x for x in row])) for row in
            self.dbs.select_all_from(Building)]

    def initialize(self, raw_data):
        tmp_building_data: DataFrame = DataFrame()

        for data in raw_data:
            if len(tmp_building_data) == 0:
                tmp_building_data = data
            else:
                tmp_building_data = (
                    merge_asof(tmp_building_data.sort_values('longitude'), data.sort_values('longitude'),
                               on='longitude', direction='nearest', tolerance=0.000009, suffixes=('', '_'))
                )

        tmp_building_data = filter_buildings(tmp_building_data)
        [self.building_data.append(Building(row)) for row in tmp_building_data.itertuples()]

    def persist(self):
        self.dbs.write_data_to_database(self.building_data)
        self.dbs.run_sql_file('\\resources\\scripts\\building_view.sql')

