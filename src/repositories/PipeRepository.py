from _decimal import Decimal

from models.data.Pipe import PipeDB, Pipe
from models.data.Point import PointDB, Point


class PipeRepository:
    def __init__(self, data_base_service):
        self.dbs = data_base_service
        self.point_data = []
        self.pipe_path_data = []
        self.shortest_path_data = []

    def initializeDB(self):
        [self.point_data.append(
            PointDB([float(x) if isinstance(x, Decimal) else x for x in row])) for row in
            self.dbs.select_all_from(Point)]

        [self.pipe_path_data.append(
            PipeDB([float(x) if isinstance(x, Decimal) else x for x in row])) for row in
            self.dbs.select_all_from(Pipe)]

    def initialize(self, raw_point_data, raw_path_data):
        [self.point_data.append(Point(row)) for row in raw_point_data.itertuples()]
        [self.pipe_path_data.append(Pipe(row)) for row in raw_path_data.itertuples(index=False)]

    def deleteAll(self):
        self.dbs.delete_all_from(Pipe)
        self.dbs.delete_all_from(Point)

    def persist_points(self):
        self.dbs.write_data_to_database(self.point_data)

    def persist_paths(self):
        self.dbs.write_data_to_database(self.pipe_path_data)

    def persist_shortest_paths(self):
        self.dbs.write_data_to_database(self.shortest_path_data)
