from _decimal import Decimal

from models.data.PipePathData import PipePathDataRaw, PipePathDataDB
from models.data.PipePointData import PipePointDataRaw, PipePointDataDB


class PipeRepository:
    def __init__(self, data_base_service):
        self.dbs = data_base_service
        self.pipe_point_data = []
        self.pipe_path_data = []
        self.shortest_path_data = []

    def initializeDB(self):
        [self.pipe_point_data.append(
            PipePointDataDB([float(x) if isinstance(x, Decimal) else x for x in row])) for row in
            self.dbs.select_all_from('pipe_point')]

        [self.pipe_path_data.append(
            PipePathDataDB([float(x) if isinstance(x, Decimal) else x for x in row])) for row in
            self.dbs.select_all_from('pipe_path')]

    def initialize(self, raw_point_data, raw_path_data):
        [self.pipe_point_data.append(PipePointDataRaw(row)) for row in raw_point_data.itertuples(index=False)]
        [self.pipe_path_data.append(PipePathDataRaw(row)) for row in raw_path_data.itertuples(index=False)]

    def deleteAll(self):
        self.dbs.delete_all_from('pipe_path')
        self.dbs.delete_all_from('pipe_point')

    def persist_points(self):
        self.dbs.write_data_to_database('pipe_point', self.pipe_point_data[0].__dict__, self.pipe_point_data)

    def persist_paths(self):
        self.dbs.write_data_to_database('pipe_path', self.pipe_path_data[0].__dict__, self.pipe_path_data)

    def persist_shortest_paths(self):
        self.dbs.write_data_to_database('shortest_path_connector', self.shortest_path_data[0].__dict__, self.shortest_path_data)
