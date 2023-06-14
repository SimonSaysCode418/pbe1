from _decimal import Decimal

from models.raw.building.RawBuildingAddress import RawBuildingAddress, RawBuildingAddressDB
from models.raw.building.RawBuildingHeight import RawBuildingHeight, RawBuildingHeightDB
from models.raw.building.RawBuildingThermosData import RawBuildingThermosData, RawBuildingThermosDataDB
from models.raw.pipe.PipePathRaw import RawPipePath, RawPipePathDB
from models.raw.pipe.PipePointRaw import RawPipePoint, RawPipePointDB


class RawDataRepository:
    def __init__(self, data_base_service):
        self.dbs = data_base_service
        self.raw_building_data: list = []
        self.raw_address_data: list = []
        self.raw_height_data: list = []
        self.raw_pipe_point_data: list = []
        self.raw_pipe_path_data: list = []

    def initialize(self):
        [self.raw_building_data.append(
            RawBuildingThermosDataDB([float(x) if isinstance(x, Decimal) else x for x in row])) for row in
            self.dbs.select_all_from('raw_building')]

        [self.raw_address_data.append(
            RawBuildingAddressDB([float(x) if isinstance(x, Decimal) else x for x in row])) for row in
            self.dbs.select_all_from('raw_address')]

        [self.raw_height_data.append(
            RawBuildingHeightDB([float(x) if isinstance(x, Decimal) else x for x in row])) for row in
            self.dbs.select_all_from('raw_height')]

        [self.raw_pipe_point_data.append(
            RawPipePointDB([float(x) if isinstance(x, Decimal) else x for x in row])) for row in
            self.dbs.select_all_from('raw_pipe_point')]

        [self.raw_pipe_path_data.append(
            RawPipePathDB([float(x) if isinstance(x, Decimal) else x for x in row])) for row in
            self.dbs.select_all_from('raw_pipe_path')]

    def set_raw_data(self, data_object):
        if isinstance(data_object, RawBuildingThermosData):
            self.raw_building_data.append(data_object)

        elif isinstance(data_object, RawBuildingAddress):
            self.raw_address_data.append(data_object)

        elif isinstance(data_object, RawBuildingHeight):
            self.raw_height_data.append(data_object)

        elif isinstance(data_object, RawPipePoint):
            self.raw_pipe_point_data.append(data_object)

        elif isinstance(data_object, RawPipePath):
            self.raw_pipe_path_data.append(data_object)

    def persist(self):
        self.dbs.write_data_to_database('raw_building', self.raw_building_data[0].__dict__, self.raw_building_data)
        self.dbs.write_data_to_database('raw_address', self.raw_address_data[0].__dict__, self.raw_address_data)
        self.dbs.write_data_to_database('raw_height', self.raw_height_data[0].__dict__, self.raw_height_data)
        self.dbs.write_data_to_database('raw_pipe_point', self.raw_pipe_point_data[0].__dict__,
                                        self.raw_pipe_point_data)
        self.dbs.write_data_to_database('raw_pipe_path', self.raw_pipe_path_data[0].__dict__, self.raw_pipe_path_data)
