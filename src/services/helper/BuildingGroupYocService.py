import os
import pandas as pd


class BuildingGroupYocService:

    def __init__(self):
        self.data = pd.read_excel(os.getcwd() + '\\resources\\inputs\\Gebäudezuordnung.xlsx',
                                  converters={'housenumber': str})
        self.data.drop_duplicates(subset=['street', 'housenumber'], keep='first', inplace=True)
        self.last_result = None

    def get_year_of_construction(self, building):
        data = self.data
        condition = (data['street'] == building.street) & (data['housenumber'] == building.housenumber)
        self.last_result = data.loc[condition]

        return int(self.last_result['year_of_construction'].values[0])

    def get_building_group(self):
        return self.last_result['groupname'].values[0]
