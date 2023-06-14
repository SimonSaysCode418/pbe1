from database.postgresql import DataBaseService
from repositories.PipeRepository import PipeRepository


class PipeService:
    def __init__(self):
        self.dbs = DataBaseService()
        self.dbs.create_pipe_tables()
        self.pr = PipeRepository(self.dbs)

    def __del__(self):
        del self.dbs
        del self.pr

    def initialize(self, raw_data_service):
        self.pr.deleteAll()
        self.pr.initialize(raw_data_service.get_raw_pipe_point_data(), raw_data_service.get_raw_pipe_path_data())

    def initializeDB(self):
        self.pr.initializeDB()

    def get_pipe_point_data(self):
        return self.pr.pipe_point_data

    def set_pipe_point_data(self, pipe_points):
        self.pr.pipe_point_data = pipe_points
        self.pr.persist_points()

    def get_pipe_path_data(self):
        return self.pr.pipe_path_data

    def set_pipe_path_data(self, pipe_paths):
        self.pr.pipe_path_data = pipe_paths
        self.pr.persist_paths()

    def set_shortest_path_connector_data(self, shortest_paths):
        self.pr.shortest_path_data = shortest_paths
        self.pr.persist_shortest_paths()
