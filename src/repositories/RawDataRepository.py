from _decimal import Decimal

from models.raw.building.RawBuildingAddress import RawBuildingAddress, RawBuildingAddressDB
from models.raw.building.RawBuildingHeight import RawBuildingHeight, RawBuildingHeightDB
from models.raw.building.RawBuildingThermosData import RawBuildingThermosData, RawBuildingThermosDataDB
from models.raw.pipe.RawPipe import RawPipe, RawPipeDB
from models.raw.pipe.RawPoint import RawPoint, RawPointDB


class RawDataRepository:
    def __init__(self, data_base_service):
        self.dbs = data_base_service
        self.raw_thermos_data: list = []
        self.raw_address_data: list = []
        self.raw_height_data: list = []
        self.raw_point_data: list = []
        self.raw_pipe_data: list = []

    def initialize(self):
        [self.raw_thermos_data.append(
            RawBuildingThermosDataDB([float(x) if isinstance(x, Decimal) else x for x in row])) for row in
            self.dbs.select_all_from(RawBuildingThermosData)]

        [self.raw_address_data.append(
            RawBuildingAddressDB([float(x) if isinstance(x, Decimal) else x for x in row])) for row in
            self.dbs.select_all_from(RawBuildingAddress)]

        [self.raw_height_data.append(
            RawBuildingHeightDB([float(x) if isinstance(x, Decimal) else x for x in row])) for row in
            self.dbs.select_all_from(RawBuildingHeight)]

        [self.raw_point_data.append(
            RawPointDB([float(x) if isinstance(x, Decimal) else x for x in row])) for row in
            self.dbs.select_all_from(RawPoint)]

        [self.raw_pipe_data.append(
            RawPipeDB([float(x) if isinstance(x, Decimal) else x for x in row])) for row in
            self.dbs.select_all_from(RawPipe)]

    def set_raw_data(self, data_object):
        if isinstance(data_object, RawBuildingThermosData):
            self.raw_thermos_data.append(data_object)

        elif isinstance(data_object, RawBuildingAddress):
            self.raw_address_data.append(data_object)

        elif isinstance(data_object, RawBuildingHeight):
            self.raw_height_data.append(data_object)

        elif isinstance(data_object, RawPoint):
            self.raw_point_data.append(data_object)

        elif isinstance(data_object, RawPipe):
            self.raw_pipe_data.append(data_object)

    def persist(self):
        self.dbs.write_data_to_database(self.raw_thermos_data)
        self.dbs.write_data_to_database(self.raw_address_data)
        self.dbs.write_data_to_database(self.raw_height_data)
        self.dbs.write_data_to_database(self.raw_point_data)
        self.dbs.write_data_to_database(self.raw_pipe_data)
