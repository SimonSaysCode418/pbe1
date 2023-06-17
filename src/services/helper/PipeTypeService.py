import math
import os

import pandas as pd
from services.helper.BasicParameterService import BasicParameterService


class PipeTypeService:

    def __init__(self, basic_parameter_service):
        self.bps: BasicParameterService = basic_parameter_service

        self.pipe_types = {}
        sheet_names = ['PMR', 'PMR-Duo', 'KMR', 'KMR-Duo']
        for sheet_name in sheet_names:
            self.pipe_types[sheet_name] = pd.read_excel(os.getcwd() + '\\resources\\parameters\\DN_Rohrdurchmesser.xlsx',
                                                        sheet_name=sheet_name)

    def get_pipe_element(self, diameter):
        pipe_type_priority = ['PMR-Duo', 'PMR', 'KMR-Duo', 'KMR']

        pipe_insulation_init = self.bps.get_parameter_value('Rohrauswahl', 'Initiale Dämmung')

        for pipe_type in pipe_type_priority:
            filtered_types = self.pipe_types[pipe_type]
            pipes = filtered_types.loc[(filtered_types['Innendurchmesser'] >= diameter)].to_dict(orient='records')
            if pipes:
                pipe = pipes[0]
                return [pipe_type, pipe['Nennweite'], pipe_insulation_init, pipe['Innendurchmesser']]
        return None

    def get_pipe_element_next_size(self, pipe_type, nominal_size):
        filtered_types = self.pipe_types[pipe_type]
        pipe = filtered_types.loc[(filtered_types['Nennweite'] == nominal_size)].to_dict(orient='records')[0]
        return self.get_pipe_element(pipe['Innendurchmesser'] + 0.0001)  # 0.0001 für nächste Rohrgröße

    def get_inner_diameter(self, type, nominal_size):
        filtered_types = self.pipe_types[type]
        pipes = filtered_types.loc[(filtered_types['Nennweite'] == nominal_size)].to_dict(orient='records')

        pipe = pipes[0]

        return pipe['Innendurchmesser']

    def get_heat_loss(self, type, nominal_size, insulation):
        filtered_types = self.pipe_types[type]
        pipes = filtered_types.loc[(filtered_types['Nennweite'] == nominal_size)].to_dict(orient='records')

        pipe = pipes[0]

        return pipe[insulation + '-W']

    def get_relative_pipe_roughness_D_k(self, inner_diameter):
        return inner_diameter / self.bps.get_parameter_value('Rohrauswahl', 'Rohrrauheit k (mm)')

    def get_relative_pipe_roughness_k_D(self, inner_diameter):
        return self.bps.get_parameter_value('Rohrauswahl', 'Rohrrauheit k (mm)') / inner_diameter

    def get_minimum_hydraulically_smooth(self):
        return self.bps.get_parameter_value('Rohrauswahl', 'Untergrenze Hydraulisch glatt')

    def get_limit_hydraulically_smooth(self, inner_diameter):
        return self.get_relative_pipe_roughness_D_k(inner_diameter) * math.log(
            0.1 * self.get_relative_pipe_roughness_D_k(inner_diameter))

    def get_limit_transitional_area(self, inner_diameter):
        return 400 * self.get_relative_pipe_roughness_D_k(inner_diameter) * math.log(
            3.715 * self.get_relative_pipe_roughness_D_k(inner_diameter))
