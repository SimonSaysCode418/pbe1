import os
import pandas as pd


class IWUService:

    def __init__(self):
        self.iwu_data = pd.read_excel(os.getcwd() + '\\resources\\Waermebedarfskennwerte (IWU).xlsx',
                                      sheet_name='Projektinput')

    def get_iwu_value(self, type, yoc, name):
        type = 'Residential' if (type.startswith('Fire Department')) | (type == 'Commerce') else type
        return self.iwu_data.loc[(self.iwu_data['Typ'] == type) &
                                 (self.iwu_data['Startjahr'] <= yoc) &
                                 (self.iwu_data['Endjahr'] >= yoc), name].values[0]
