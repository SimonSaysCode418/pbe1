from services.database.DataBaseService import DataBaseService
from models.data.Pipe import Pipe
from models.data.Point import Point
from models.data.ShortestPathConnector import ShortestPathConnector
from repositories.PipeRepository import PipeRepository


class PipeService:
    def __init__(self):
        self.dbs = DataBaseService()
        self.pr = PipeRepository(self.dbs)

    def __del__(self):
        del self.dbs
        del self.pr

    def initialize(self, raw_data_service):
        self.dbs.create_table_from_class(Point)
        self.dbs.create_table_from_class(Pipe)
        self.dbs.create_table_from_class(ShortestPathConnector)
        self.pr.initialize(raw_data_service.get_raw_point_data(), raw_data_service.get_raw_pipe_data())

    def initializeDB(self):
        self.pr.initializeDB()

    def get_point_data(self):
        return self.pr.point_data

    def set_point_data(self, points):
        self.pr.point_data = points
        self.pr.persist_points()

    def get_pipe_data(self):
        return self.pr.pipe_path_data

    def set_pipe_data(self, pipes):
        self.pr.pipe_path_data = pipes
        self.pr.persist_paths()

    def set_shortest_path_connector_data(self, shortest_paths):
        self.pr.shortest_path_data = shortest_paths
        self.pr.persist_shortest_paths()
