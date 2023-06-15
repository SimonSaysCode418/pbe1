import os
import pandas as pd


class BasicParameterService:

    def __init__(self):
        df = pd.read_excel(os.getcwd() + '\\resources\\parameters\\Parameter.xlsx')
        self.parameters = {}

        for index, row in df.iterrows():
            kategorie = row['Kategorie']
            name = row['Parameter']
            wert = row['Wert']

            if not pd.isna(kategorie) and not kategorie.startswith('#'):
                if kategorie not in self.parameters:
                    self.parameters[kategorie] = {}  # Neue Kategorie erstellen
                self.parameters[kategorie][name] = wert

    def get_parameter_kategorie(self, kategorie):
        return self.parameters.get(kategorie)

    def get_parameter_value(self, kategorie, name):
        return self.parameters.get(kategorie).get(name)
